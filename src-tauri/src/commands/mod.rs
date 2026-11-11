use std::sync::Mutex;

use serde::Serialize;
use tauri::State;
use tauri_plugin_shell::process::CommandChild;

#[derive(Clone, Serialize)]
pub struct BackendConfig {
    pub port: u16,
    pub token: String,
}

pub struct BackendState {
    pub config: BackendConfig,
    pub child: Mutex<Option<CommandChild>>,
}

/// Lets the React app discover the dynamic port and per-launch secret.
#[tauri::command]
pub fn get_backend_config(state: State<'_, BackendState>) -> BackendConfig {
    state.config.clone()
}
