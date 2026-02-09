import { supabase } from '@/lib/supabase'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

// Create a custom fetch client that adds auth headers
async function fetchClient<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    // Get Supabase Session token
    const { data } = await supabase.auth.getSession()
    const token = data.session?.access_token

    // Construct Headers
    const headers = new Headers(options.headers);
    headers.set('Content-Type', 'application/json');

    if (token) {
        headers.set('Authorization', `Bearer ${token}`);
    }

    const config: RequestInit = {
        ...options,
        headers,
    };

    const response = await fetch(`${API_BASE_URL}${endpoint}`, config);

    if (!response.ok) {
        const errorBody = await response.text();
        throw new Error(`API Error: ${response.status} - ${errorBody}`);
    }

    // Handle empty responses (like 204 No Content)
    if (response.status === 204) {
        return {} as T;
    }

    return response.json();
}

// --- API Methods ---

export interface FlowState {
    state: 'FLOW' | 'IDLE' | 'SHALLOW';
}

export interface StateResponse {
    state: FlowState['state'];
    user_id: string;
}

export interface Task {
    id: string;
    title: string;
    summary?: string;
    suggested_action?: string;
    urgency: number;
    estimated_minutes?: number;
    deadline?: string;
    status: 'pending' | 'in_progress' | 'completed' | 'blocked' | 'deferred';
    priority_score: number;
    context_tags: string[];
    created_at: string;
    completed_at?: string;
}

export interface TaskCreateRequest {
    title: string;
    summary?: string;
    suggested_action?: string;
    urgency?: number;
    estimated_minutes?: number;
    deadline?: string;
    context_tags?: string[];
}

export interface QueueResponse {
    current_task: Task | null;
    queue: Task[];
    total_count: number;
}

export interface DailyStats {
    deep_work_minutes: number;
    context_switches: number;
    tasks_completed: number;
    tasks_intercepted: number;
    flow_sessions: number;
}

export const api = {
    // Generic get method for any endpoint
    get: <T>(endpoint: string) => fetchClient<T>(endpoint),

    state: {
        get: () => fetchClient<StateResponse>('/state'),
        update: (state: FlowState['state']) =>
            fetchClient<StateResponse>('/state', {
                method: 'PUT',
                body: JSON.stringify({ state })
            }),
    },
    queue: {
        get: () => fetchClient<QueueResponse>('/queue'),
        create: (task: TaskCreateRequest) =>
            fetchClient<Task>('/queue', {
                method: 'POST',
                body: JSON.stringify(task)
            }),
        history: (limit: number = 20, offset: number = 0) =>
            fetchClient<Task[]>(`/queue/history?limit=${limit}&offset=${offset}`),
    },
    stats: {
        daily: () => fetchClient<DailyStats>('/stats/daily'),
    },
};
