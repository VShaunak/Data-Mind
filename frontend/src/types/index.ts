export interface ColumnProfile {
  name: string;
  dtype: string;
  null_count: number;
  null_percentage: number;
  unique_count: number;
  type_category?: 'numeric' | 'categorical' | 'datetime' | 'string';
  min?: any;
  max?: any;
}

export interface DatasetProfile {
  file_name: string;
  file_path: string;
  format: string;
  sheet_name?: string;
  row_count: number;
  column_count: number;
  duplicate_rows: number;
  memory_usage: string;
  columns: ColumnProfile[];
  numerical_summaries: Record<string, {
    mean: number | null;
    std: number | null;
    min: number | null;
    '25%': number | null;
    '50%': number | null;
    '75%': number | null;
    max: number | null;
  }>;
  categorical_summaries: Record<string, Record<string, number>>;
  datetime_columns: string[];
  sample_data: Record<string, any>[];
}

export interface Session {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
  dataset_path?: string;
  dataset_name?: string;
  dataset_profile?: DatasetProfile;
  selected_provider?: string;
  selected_model?: string;
  status: 'idle' | 'running' | 'completed' | 'failed';
}

export interface Task {
  id: string;
  session_id: string;
  prompt: string;
  created_at: string;
  completed_at?: string;
  status: 'running' | 'completed' | 'failed' | 'partial_success';
  plan?: Record<string, any>;
  code?: string;
  error_message?: string;
  traceback?: string;
  attempt_count: number;
  stdout?: string;
  stderr?: string;
  chart_json?: any;
  report_json?: {
    metrics?: Record<string, any>;
    report_markdown?: string;
  };
  duration_seconds: number;
}

export interface Artifact {
  id: string;
  session_id: string;
  task_id?: string;
  artifact_type: 'chart' | 'report' | 'code' | 'dataset' | 'export';
  name: string;
  file_path: string;
  content?: string;
  created_at: string;
}

export interface ExecutionEvent {
  session_id: string;
  task_id?: string;
  stage: string;
  status: 'running' | 'completed' | 'failed';
  message: string;
  metadata?: Record<string, any>;
  timestamp: string;
}

export interface ModelInfo {
  id: string;
  name: string;
  provider: string;
  size?: string;
  context_length?: number;
}

export interface ProviderStatus {
  available: boolean;
  base_url: string;
  models: ModelInfo[];
}

export interface DiagnosticsData {
  app_name: string;
  app_version: string;
  os_info: {
    platform: string;
    platform_release: string;
    platform_version: string;
    architecture: string;
    python_version: string;
    python_executable: string;
  };
  storage: {
    home_path: string;
    db_path: string;
    writable: boolean;
    error: string | null;
    free_disk_gb: number;
  };
  docker: {
    docker_available: boolean;
    docker_error: string | null;
    wsl2_installed: boolean;
    sandbox_mode: string;
  };
  providers: Record<string, ProviderStatus>;
  default_provider: string;
  default_model: string;
  overall_status: string;
}

