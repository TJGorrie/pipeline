from luigi_classes import data_in_proasis
import luigi
import os

from luigi_classes import ligand_analysis


class KickOff(luigi.Task):
    def output(self):
        return luigi.LocalTarget('pipeline.done')

    def requires(self):
        try:
            # os.system('./pg_backup.sh')
            os.system('rm logs/ligand_search.done')
            os.system('rm logs/pipeline.done')
            os.system('rm /dls/science/groups/i04-1/software/luigi_pipeline/logs/hits.done')
            os.system('rm /dls/science/groups/i04-1/software/luigi_pipeline/logs/leads.done')
            os.system('rm /dls/science/groups/i04-1/software/luigi_pipeline/logs/transfer.txt')
            os.system('rm /dls/science/groups/i04-1/software/luigi_pipeline/logs/hits.done')
            os.system('rm /dls/science/groups/i04-1/software/luigi_pipeline/logs/findprojects.done')
            os.system('rm /dls/science/groups/i04-1/software/luigi_pipeline/logs/blacklists.done')
            os.system('rm /dls/science/groups/i04-1/software/luigi_pipeline/logs/edstats.done')
        except:
            print('Whoops...')

        return data_in_proasis.WriteBlackLists(), ligand_analysis.StartEdstatsScores()

    def run(self):
        with self.output().open('wb') as f:
            f.write('')