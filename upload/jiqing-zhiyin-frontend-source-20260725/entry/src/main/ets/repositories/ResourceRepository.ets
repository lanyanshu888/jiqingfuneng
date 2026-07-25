import { ApiError } from '../core/http/ApiError';
import { networkState } from '../core/network/NetworkState';
import { Environment } from '../core/config/Environment';
import { apiClient } from '../core/http/ApiProvider';
import { GrowthRecords } from '../models/PlanModels';
import { GrowthResource, ResourceListResponse, ResourceType } from '../models/ResourceModels';
import { RECORDS_FIXTURE, RESOURCES_FIXTURE } from '../mock/MockFixtures';

export class ResourceRepository {
  private resources: GrowthResource[] = RESOURCES_FIXTURE;
  private records: GrowthRecords = RECORDS_FIXTURE;

  async list(type: ResourceType): Promise<GrowthResource[]> {
    if (!Environment.MOCK_MODE) {
      const response = await apiClient.get<ResourceListResponse>(`/${this.pathFor(type)}/`);
      return response.items;
    }
    return this.resources.filter((item) => item.resourceType === type);
  }

  async detail(type: ResourceType, id: number): Promise<GrowthResource> {
    if (!Environment.MOCK_MODE) {
      return apiClient.get<GrowthResource>(`/${this.pathFor(type)}/${id}/`);
    }
    const resource = this.resources.find((item) => item.resourceType === type && item.id === id);
    if (!resource) {
      throw new ApiError(404, '资源不存在');
    }
    return resource;
  }

  async toggleFavorite(type: ResourceType, id: number): Promise<boolean> {
    this.ensureOnline();
    if (!Environment.MOCK_MODE) {
      const response = await apiClient.post<{ favorited: boolean }>('/favorites/toggle/', {
        resourceType: type,
        resourceId: id
      });
      return response.favorited;
    }
    let favorited = false;
    this.resources = this.resources.map((item) => {
      if (item.resourceType === type && item.id === id) {
        favorited = !item.favorited;
        return this.copyResource(item, favorited, item.actionState);
      }
      return item;
    });
    return favorited;
  }

  async applyOpportunity(id: number): Promise<void> {
    this.ensureOnline();
    if (!Environment.MOCK_MODE) {
      await apiClient.post<object>(`/opportunities/${id}/enroll/`, {});
      return;
    }
    this.markAction('opportunity', id, '已申请');
    this.records = {
      favorites: this.records.favorites,
      applications: this.records.applications + 1,
      enrollments: this.records.enrollments,
      completedCourses: this.records.completedCourses,
      consultations: this.records.consultations
    };
  }

  async enrollActivity(id: number): Promise<void> {
    this.ensureOnline();
    if (!Environment.MOCK_MODE) {
      await apiClient.post<object>(`/activities/${id}/enroll/`, {});
      return;
    }
    this.markAction('activity', id, '已报名');
    this.records = {
      favorites: this.records.favorites,
      applications: this.records.applications,
      enrollments: this.records.enrollments + 1,
      completedCourses: this.records.completedCourses,
      consultations: this.records.consultations
    };
  }

  async completeCourse(id: number): Promise<void> {
    this.ensureOnline();
    if (!Environment.MOCK_MODE) {
      await apiClient.post<object>(`/courses/${id}/complete/`, {});
      return;
    }
    this.markAction('course', id, '已完成');
    this.records = {
      favorites: this.records.favorites,
      applications: this.records.applications,
      enrollments: this.records.enrollments,
      completedCourses: this.records.completedCourses + 1,
      consultations: this.records.consultations
    };
  }

  async consultMentor(id: number, scheduledAt: string, question: string): Promise<void> {
    this.ensureOnline();
    if (!Environment.MOCK_MODE) {
      await apiClient.post<object>(`/mentors/${id}/consult/`, {
        scheduledAt,
        question
      });
      return;
    }
    this.markAction('mentor', id, '已预约');
    this.records = {
      favorites: this.records.favorites,
      applications: this.records.applications,
      enrollments: this.records.enrollments,
      completedCourses: this.records.completedCourses,
      consultations: this.records.consultations + 1
    };
  }

  async growthRecords(): Promise<GrowthRecords> {
    if (!Environment.MOCK_MODE) {
      return apiClient.get<GrowthRecords>('/me/growth/');
    }
    return this.records;
  }

  private pathFor(type: ResourceType): string {
    if (type === 'policy') {
      return 'policies';
    }
    if (type === 'opportunity') {
      return 'opportunities';
    }
    if (type === 'course') {
      return 'courses';
    }
    if (type === 'activity') {
      return 'activities';
    }
    return 'mentors';
  }

  private markAction(type: ResourceType, id: number, actionState: string): void {
    this.resources = this.resources.map((item) => {
      if (item.resourceType === type && item.id === id) {
        return this.copyResource(item, item.favorited, actionState);
      }
      return item;
    });
  }

  private ensureOnline(): void {
    if (!networkState.isOnline()) {
      throw new ApiError(0, '当前离线，联网后才能完成此操作');
    }
  }

  private copyResource(resource: GrowthResource, favorited: boolean, actionState?: string): GrowthResource {
    return {
      id: resource.id,
      resourceType: resource.resourceType,
      title: resource.title,
      region: resource.region,
      category: resource.category,
      description: resource.description,
      deadline: resource.deadline,
      startsAt: resource.startsAt,
      tags: resource.tags,
      reasons: resource.reasons,
      sourceUrl: resource.sourceUrl,
      favorited,
      actionState
    };
  }
}
