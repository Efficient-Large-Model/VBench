import os

from vbench2_beta_i2v.utils import init_submodules, save_json, load_json
from vbench import VBench
import importlib
from vbench.distributed import get_rank, print0

class VBenchI2V(VBench):
    def __init__(self, device, full_info_dir, output_path):
        super().__init__(device, full_info_dir, output_path)
        self.i2v_dims = ["i2v_subject", "i2v_background", "camera_motion"]
        self.quality_dims = ["subject_consistency", "background_consistency", "aesthetic_quality", "imaging_quality", "temporal_flickering", "motion_smoothness", "dynamic_degree",]
        
    def build_full_dimension_list(self, ):
        return self.i2v_dims + self.quality_dims

    def evaluate(self, videos_path, name, dimension_list=None, custom_image_folder=None, mode='vbench_standard', local=False, read_frame=False, resolution="1-1", **kwargs):
        results_dict = {}
        if dimension_list is None:
            dimension_list = self.build_full_dimension_list()
        submodules_dict = init_submodules(dimension_list, local=local, read_frame=read_frame, resolution=resolution)
        # print0('BEFORE BUILDING')
        cur_full_info_path = self.build_full_info_json(videos_path, name, dimension_list, custom_image_folder=custom_image_folder, mode=mode)
        # print0('AFTER BUILDING')
        for dimension in dimension_list:
            try:
                if dimension in self.i2v_dims:
                    dimension_module = importlib.import_module(f'vbench2_beta_i2v.{dimension}')
                else:
                    dimension_module = importlib.import_module(f'vbench.{dimension}')
                evaluate_func = getattr(dimension_module, f'compute_{dimension}')
            except Exception as e:
                raise NotImplementedError(f'UnImplemented dimension {dimension}!, {e}')
            submodules_list = submodules_dict[dimension]
            print0(f'cur_full_info_path: {cur_full_info_path}') # TODO: to delete
            results = evaluate_func(cur_full_info_path, self.device, submodules_list, **kwargs)
            results_dict[dimension] = results
        output_name = os.path.join(self.output_path, name+'_eval_results.json')
        if get_rank() == 0:
            save_json(results_dict, output_name)
            print0(f'Evaluation results saved to {output_name}')
