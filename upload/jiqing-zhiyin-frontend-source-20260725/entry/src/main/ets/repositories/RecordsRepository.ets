import { GrowthRecords } from '../models/PlanModels';
import { ResourceRepository } from './ResourceRepository';

export class RecordsRepository {
  private resourceRepository: ResourceRepository = new ResourceRepository();

  async list(): Promise<GrowthRecords> {
    return this.resourceRepository.growthRecords();
  }
}

