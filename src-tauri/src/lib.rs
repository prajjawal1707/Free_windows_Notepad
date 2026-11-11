mod commands;

use std::net::TcpListener;
use std::sync::Mutex;

use tauri::{Manager, RunEvent};
use tauri_plugin_shell::{process::{CommandChild, CommandEvent}, ShellExt};

use commands::{get_backend_config, BackendConfig, BackendState};

/// Ask the OS for a free loopback port.
fn free_port() -> u16 {
    TcpListener::bind("127.0.0.1:0")
        .and_then(|l| l.local_addr())
        .map(|a| a.port())
        .expect("no free local port")
}

fn random_token() -> String {
    format!("{}{}", uuid::Uuid::new_v4().simple(), uuid::Uuid::new_v4().simple())
}

pub fn run() {
    let app = tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .invoke_handler(tauri::generate_handler![get_backend_config])
        .setup(|app| {
            let data_dir = app.path().app_data_dir()?; // survives app updates
            std::fs::create_dir_all(&data_dir)?;

            let (config, child): (BackendConfig, Option<CommandChild>) = if cfg!(debug_assertions) {
                // `tauri dev`: run the backend yourself with `npm run dev:backend`
                (BackendConfig { port: 8765, token: "dev-token".into() }, None)
            } else {
                let config = BackendConfig { port: free_port(), token: random_token() };
                let (mut rx, child) = app
                    .shell()
                    .sidecar("backend")?
                    .args([
                        "--port", &config.port.to_string(),
                        "--token", &config.token,
                        "--data-dir", &data_dir.to_string_lossy(),
                        "--parent-pid", &std::process::id().to_string(),
                    ])
                    .spawn()?;
                // Drain backend output so the pipe never fills up.
                tauri::async_runtime::spawn(async move {
                    while let Some(event) = rx.recv().await {
                        match event {
                            CommandEvent::Stdout(l) | CommandEvent::Stderr(l) => {
                                println!("[backend] {}", String::from_utf8_lossy(&l).trim_end())
                            }
                            CommandEvent::Error(e) => eprintln!("[backend error] {e}"),
                            CommandEvent::Terminated(p) => eprintln!("[backend exited] {:?}", p.code),
                            _ => {}
                        }
                    }
                });
                (config, Some(child))
            };

            app.manage(BackendState { config, child: Mutex::new(child) });
            Ok(())
        })
        .build(tauri::generate_context!())
        .expect("error while building Tauri application");

    app.run(|handle, event| {
        // Stop the Python process when the app exits.
        if let RunEvent::Exit = event {
            if let Some(state) = handle.try_state::<BackendState>() {
                if let Some(child) = state.child.lock().unwrap().take() {
                    let _ = child.kill();
                }
            }
        }
    });
}
