// TypeScript 类型定义（Day 10 完善）

export interface Task {
  id: number
  filename: string
  rows: number
  cols: number
  status: string
  created_at: string
}

export interface ColumnInfo {
  name: string
  dtype: string
  sample: string[]
  null_count: number
  unique_count: number
}

export interface UploadResponse {
  id: number
  filename: string
  rows: number
  cols: number
  columns: ColumnInfo[]
  status: string
  message: string
}
