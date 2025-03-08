import axios from 'axios';

export interface ProjectSummary {
  type: 'summary';
  standup: string;
  project: any;
}

export interface ApiResponse {
  success: boolean;
  message?: string;
  speech_segments?: string[];
  stage?: string;
  data?: any;
  summaryData?: ProjectSummary;
  transcript?: string;
}

class Api {
  private baseUrl = '/api';  // Use relative URL to work with any host

  async startConversation(): Promise<ApiResponse> {
    try {
      const response = await axios.get(`${this.baseUrl}/start`);
      return response.data;
    } catch (error) {
      console.error('Error starting conversation:', error);
      return { success: false, message: 'Failed to start conversation' };
    }
  }

  async sendMessage(text: string, stage: string): Promise<ApiResponse> {
    try {
      const response = await axios.post(`${this.baseUrl}/chat`, {
        message: text,
        stage
      });
      return response.data;
    } catch (error) {
      console.error('Error sending message:', error);
      return { success: false, message: 'Failed to send message' };
    }
  }

  async speak(text: string): Promise<Blob | null> {
    try {
      const response = await axios.post(
        `${this.baseUrl}/speak`,
        { text },
        { responseType: 'blob' }
      );
      return new Blob([response.data], { type: 'audio/wav' });  // Use WAV type
    } catch (error) {
      console.error('Error converting text to speech:', error);
      return null;
    }
  }

  async processAudio(audioBlob: Blob, stage: string): Promise<ApiResponse> {
    try {
      const formData = new FormData();
      formData.append('audio', audioBlob);
      formData.append('stage', stage);

      const response = await axios.post(`${this.baseUrl}/audio`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return response.data;
    } catch (error) {
      console.error('Error processing audio:', error);
      return { success: false, message: 'Failed to process audio' };
    }
  }

  async getProjectSummary(projectKey: string = 'SCRUM'): Promise<ApiResponse> {
    try {
      const response = await axios.get(`${this.baseUrl}/project-summary`, {
        params: { projectKey }
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching project summary:', error);
      return { success: false, message: 'Failed to fetch project summary' };
    }
  }

  async getTodoTasks(): Promise<any[]> {
    try {
      const response = await axios.get(`${this.baseUrl}/get_todo_tasks`);
      return response.data.tasks || [];
    } catch (error) {
      console.error('Error getting TODO tasks:', error);
      return [];
    }
  }
}

export const api = new Api();
