export interface CapacityInfo {
  image_dimensions: [number, number];
  total_blocks: number;
  repetition_factor: number;
  overhead_bytes: number;
  overhead_blocks: number;
  max_payload_bytes: number;
  is_feasible: boolean;
  recommended_min_dimension: number;
}

export interface RecoveryManifest {
  algorithm: string;
  version: number;
  block_size: number;
  middle_band: number[];
  strength_profile: string;
  quantization_step: number;
  repetition_factor: number;
  parity_bytes: number;
  codeword_bits_count: number;
  total_embedded_bits: number;
  original_dimensions: [number, number];
  padded_dimensions: [number, number];
  image_mode: string;
  has_alpha: boolean;
}

export interface EmbedMetrics {
  execution_time_seconds: number;
  psnr_db: number;
  ssim: number;
  total_blocks: number;
  utilized_blocks: number;
  utilization_percentage: number;
  codeword_bytes: number;
  payload_bytes: number;
}

export interface EmbedResult {
  job_id: string;
  status: string;
  watermarked_image_url: string;
  recovery_manifest: RecoveryManifest;
  metrics: EmbedMetrics;
  image_info: {
    width: number;
    height: number;
    format: string;
  };
}

export interface ExtractResult {
  job_id: string;
  status: "success" | "corrupted" | "not_detected" | "invalid_manifest" | "key_error" | "dimension_mismatch";
  success: boolean;
  recovered_message?: string | null;
  mean_confidence?: number | null;
  fec_status?: string | null;
  ber_percentage?: number | null;
  nc?: number | null;
  error?: string | null;
  execution_time_seconds: number;
}

export interface AttackResult {
  attack_name: string;
  parameters: Record<string, any>;
  attacked_image_url: string;
  psnr_db: number;
  ssim: number;
  extraction_status: string;
  extraction_success: boolean;
  recovered_message?: string | null;
  mean_confidence?: number | null;
  ber_percentage?: number | null;
  nc?: number | null;
  execution_time: number;
}

export interface JobRecord {
  id: string;
  operation_type: "embed" | "extract";
  status: string;
  image_width?: number;
  image_height?: number;
  image_format?: string;
  created_at?: string;
  completed_at?: string;
  metrics?: Record<string, any>;
  extracted_message?: string;
}

