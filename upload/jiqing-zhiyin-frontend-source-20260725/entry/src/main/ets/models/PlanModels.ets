export type GrowthStage = '7days' | '1month' | '3months';

export interface GrowthTask {
  id: number;
  title: string;
  description: string;
  stage: GrowthStage;
  deadlineText: string;
  completed: boolean;
}

export interface GrowthPlan {
  goal: string;
  progress: number;
  todayTask: GrowthTask;
  tasks: GrowthTask[];
}

export interface DashboardResponse {
  nickname: string;
  currentGoal: string;
  profileCompleteness: number;
  progress: number;
  suggestion: string;
  plan: GrowthPlan;
}

export interface GrowthRecords {
  favorites: number;
  applications: number;
  enrollments: number;
  completedCourses: number;
  consultations: number;
}

