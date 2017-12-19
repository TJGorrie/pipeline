import luigi
import psycopg2
import database_operations
import pandas
import datetime
import os
import misc_functions

class FindProjects(luigi.Task):

    def requires(self):
        return database_operations.TransferExperiment()

    def output(self):
        pass

    def run(self):
        # all data necessary for uploading hits
        crystal_data_dump_dict = {'crystal_name':[], 'protein':[], 'smiles':[], 'bound_conf':[], 'modification_date':[]}

        # all data necessary for uploading leads
        project_data_dump_dict = {'crystal_name':[], 'protein':[], 'pandda_path':[], 'reference_pdb':[]}

        outcome_string = '(%3%|%4%|%5%|%6%)'

        conn = psycopg2.connect('dbname=xchem user=uzw12877 host=localhost')
        c = conn.cursor()

        c.execute('''SELECT crystal_id, bound_conf FROM refinement WHERE outcome SIMILAR TO %s''', (str(outcome_string),))

        rows = c.fetchall()

        print(str(len(rows)) + ' crystals were found to be in refinement or above')

        for row in rows:

            c.execute('''SELECT smiles, protein FROM lab WHERE crystal_id = %s''', (str(row[0]),))

            lab_table = c.fetchall()

            if len(str(row[0])) < 3:
                continue

            if len(lab_table)>1:
                print('WARNING: ' + str(row[0]) + ' has multiple entries in the lab table')
                #print lab_table


            for entry in lab_table:
                if len(str(entry[1])) < 2 or 'None' in str(entry[1]):
                    protein_name = str(row[0]).split('-')[0]
                else:
                    protein_name = str(entry[1])

                if len(str(row[1])) < 5:
                    print ('No bound conf for ' + str(row[0]))
                    continue

                crystal_data_dump_dict['protein'].append(protein_name)
                crystal_data_dump_dict['smiles'].append(entry[0])
                crystal_data_dump_dict['crystal_name'].append(row[0])
                crystal_data_dump_dict['bound_conf'].append(row[1])

                try:
                    modification_date = misc_functions.get_mod_date(str(row[1]))
                except:
                    modification_date = ''

                crystal_data_dump_dict['modification_date'].append(modification_date)

            c.execute('''SELECT pandda_path, reference_pdb FROM dimple WHERE crystal_id = %s''', (str(row[0]),))

            pandda_info = c.fetchall()

            for pandda_entry in pandda_info:
                project_data_dump_dict['crystal_name'].append(row[0])
                project_data_dump_dict['protein'].append(protein_name)
                project_data_dump_dict['pandda_path'].append(pandda_entry[0])
                project_data_dump_dict['reference_pdb'].append(pandda_entry[1])

        project_table = pandas.DataFrame.from_dict(project_data_dump_dict)
        crystal_table = pandas.DataFrame.from_dict(crystal_data_dump_dict)

        protein_list=set(list(project_data_dump_dict['protein']))
        print protein_list


        for protein in protein_list:

            filename = str('leads/' + protein)
            temp_frame = project_table.loc[project_table['protein'] == protein]
            temp_frame.reset_index(inplace=True)
            temp2 = temp_frame.drop_duplicates()
            temp2.to_csv(filename)

            filename = str('hits/' + protein)
            temp_frame = crystal_table.loc[crystal_table['protein'] == protein]
            temp_frame.reset_index(inplace=True)
            temp2 = temp_frame.drop_duplicates(subset=['crystal_name','smiles','bound_conf'])
            temp2.to_csv(filename)


class WriteWhitelists(luigi.Task):
    def requires(self):
        return database_operations.TransferFedIDs()

    def output(self):
        pass

    def run(self):
        pass


class WriteFedIDList(luigi.Task):
    def requires(self):
        return database_operations.TransferFedIDs()

    def output(self):
        pass

    def run(self):
        pass