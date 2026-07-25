export type ResourceType = 'policy' | 'opportunity' | 'course' | 'activity' | 'mentor';

export interface GrowthResource {
  id: number;
  resourceType: ResourceType;
  title: string;
  region?: string;
  category?: string;
  description?: string;
  deadline?: string;
  startsAt?: string;
  tags: string[];
  reasons: string[];
  sourceUrl?: string;
  favorited: boolean;
  actionState?: string;
}

export interface ResourceListResponse {
  items: GrowthResource[];
}

