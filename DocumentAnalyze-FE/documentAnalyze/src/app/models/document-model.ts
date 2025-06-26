export interface ProcessingStage {
    name: string;
    duration: number;
    details: any;
  }
  
  export interface DocumentModel {
    id: number;
    filename: string;
    storage_path: string;
    uploaded_by: number;
    uploaded_time: string;
    classified_as: string;
    status: string;
    routed_to?: string;
    stages?: ProcessingStage[];
  }
  