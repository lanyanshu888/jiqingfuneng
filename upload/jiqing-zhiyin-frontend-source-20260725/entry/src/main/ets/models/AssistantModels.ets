export type AssistantAction =
  'profile_analysis' |
  'career_plan' |
  'policy_search' |
  'resource_match' |
  'daily_suggestion';

export interface AssistantCard {
  id: string;
  title: string;
  summary: string;
  reasons: string[];
  actionLabel?: string;
  resourceType?: string;
  resourceId?: number;
}

export interface AssistantResult {
  action: AssistantAction;
  title: string;
  message: string;
  cards: AssistantCard[];
}

