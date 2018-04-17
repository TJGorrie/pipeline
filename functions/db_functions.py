import csv
import logging
import os
import sqlite3
import subprocess
import sys

import pandas as pd
import psycopg2
from sqlalchemy import create_engine
import setup_django
from db import models
from functions import misc_functions


def connectDB():
    conn = psycopg2.connect('dbname=xchem user=uzw12877 host=localhost')
    c = conn.cursor()

    return conn, c


def column_exists(table, column):
    conn, c = connectDB()
    c.execute('''select * from information_schema.columns where table_name=%s and column_name=%s;''', (table, column))
    rows = c.fetchall()
    if len(rows)==0:
        exists = None
    else:
        exists = True
    return exists


def table_exists(c, tablename):
    c.execute('''select exists(select * from information_schema.tables where table_name=%s);''', (tablename,))
    exists = c.fetchone()[0]
    return exists


def define_lab_translations():
    # TODO: crystal_name, fileid
    lab = {
        'compound_code': 'CompoundCode',
        'cryo_frac': 'CryoFraction',
        'cryo_status': 'CryoStatus',
        'cryo_stock_frac': 'CryoStockFraction',
        'cryo_transfer_vol': 'CryoTransferVolume',
        'crystal_name': 'CrystalName',  # d['CrystalName'],
        'data_collection_visit': 'DataCollectionVisit',
        'expr_conc': 'CompoundConcentration',
        # 'file_id': [],
        'harvest_status': 'HarvestStatus',
        'library_name': 'LibraryName',
        'library_plate': 'LibraryPlate',
        'mounting_result': 'MountingResult',
        'mounting_time': 'MountingTime',
        'protein': 'ProteinName',
        'smiles': 'CompoundSMILES',
        'soak_status': 'SoakStatus',
        'soak_time': 'SoakingTime',
        'soak_vol': 'SoakTransferVol',
        'solv_frac': 'SolventFraction',
        'stock_conc': 'CompoundStockConcentration',
        'visit': 'LabVisit'
    }

    return lab

# TODO: ADD TRANSFER OF DATA TO DJANGO
def transfer_table(translate_dict, results):
    for row in results:
        d = {}
        row_keys = row.keys()
        row_values = list(tuple(row))

        for i, x in enumerate(row_keys):
            if x in dict((v, k) for k, v in translate_dict.items()).keys():
                key = dict((v, k) for k, v in translate_dict.items())[x]
                if key not in d.keys():
                    d[key] = ''
                d[key] = row_values[i]

        print(d)


def soakdb_query(filename):
    conn = sqlite3.connect(filename)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    c.execute('''select LabVisit, LibraryPlate, LibraryName, CompoundSMILES, CompoundCode,
                                            ProteinName, CompoundStockConcentration, CompoundConcentration, SolventFraction, 
                                            SoakTransferVol, SoakStatus, CryoStockFraction, CryoFraction, CryoTransferVolume, 
                                            CryoStatus, SoakingTime, HarvestStatus, CrystalName, MountingResult, MountingTime, 
                                            DataCollectionVisit, 

                                            ProjectDirectory, 

                                            CrystalTag, CrystalFormName, CrystalFormSpaceGroup,
                                            CrystalFormPointGroup, CrystalFormA, CrystalFormB, CrystalFormC,CrystalFormAlpha, 
                                            CrystalFormBeta, CrystalFormGamma, CrystalFormVolume, 

                                            DataCollectionDate, 
                                            DataCollectionOutcome, DataCollectionWavelength, 

                                            DataProcessingPathToImageFiles,
                                            DataProcessingProgram, DataProcessingSpaceGroup, DataProcessingUnitCell,
                                            DataProcessingAutoAssigned, DataProcessingResolutionOverall, DataProcessingResolutionLow,
                                            DataProcessingResolutionLowInnerShell, DataProcessingResolutionHigh, 
                                            DataProcessingResolutionHigh15Sigma, DataProcessingResolutionHighOuterShell, 
                                            DataProcessingRMergeOverall, DataProcessingRMergeLow, DataProcessingRMergeHigh, 
                                            DataProcessingIsigOverall, DataProcessingIsigLow, DataProcessingIsigHigh, 
                                            DataProcessingCompletenessOverall, DataProcessingCompletenessLow,
                                            DataProcessingCompletenessHigh, DataProcessingMultiplicityOverall, 
                                            DataProcessingMultiplicityLow, DataProcessingMultiplicityHigh, 
                                            DataProcessingCChalfOverall, DataProcessingCChalfLow, DataProcessingCChalfHigh, 
                                            DataProcessingPathToLogFile, DataProcessingPathToMTZfile, DataProcessingLOGfileName, 
                                            DataProcessingMTZfileName, DataProcessingDirectoryOriginal,
                                            DataProcessingUniqueReflectionsOverall, DataProcessingLattice, DataProcessingPointGroup,
                                            DataProcessingUnitCellVolume, DataProcessingAlert, DataProcessingScore,
                                            DataProcessingStatus, DataProcessingRcryst, DataProcessingRfree, 
                                            DataProcessingPathToDimplePDBfile, DataProcessingPathToDimpleMTZfile,
                                            DataProcessingDimpleSuccessful, 

                                            DimpleResolutionHigh, DimpleRfree, DimplePathToPDB,
                                            DimplePathToMTZ, DimpleReferencePDB, DimpleStatus, DimplePANDDAwasRun, 
                                            DimplePANDDAhit, DimplePANDDAreject, DimplePANDDApath, 

                                            PANDDAStatus, DatePANDDAModelCreated, 

                                            RefinementResolution, RefinementResolutionTL, 
                                            RefinementRcryst, RefinementRcrystTraficLight, RefinementRfree, 
                                            RefinementRfreeTraficLight, RefinementSpaceGroup, RefinementLigandCC, 
                                            RefinementRmsdBonds, RefinementRmsdBondsTL, RefinementRmsdAngles, RefinementRmsdAnglesTL,
                                            RefinementOutcome, RefinementMTZfree, RefinementCIF, RefinementCIFStatus, 
                                            RefinementCIFprogram, RefinementPDB_latest, RefinementMTZ_latest, RefinementMatrixWeight, 
                                            RefinementPathToRefinementFolder, RefinementLigandConfidence, 
                                            RefinementLigandBoundConformation, RefinementBoundConformation, RefinementMolProbityScore,
                                            RefinementMolProbityScoreTL, RefinementRamachandranOutliers, 
                                            RefinementRamachandranOutliersTL, RefinementRamachandranFavored, 
                                            RefinementRamachandranFavoredTL, RefinementStatus

                                            from mainTable 
                                            where CrystalName NOT LIKE ?
                                            and CrystalName IS NOT NULL 		
                                            and CompoundSMILES not like ? 
                                            and CompoundSMILES IS NOT NULL''',
               ('None', 'None'))

    results = c.fetchall()
    return results


def define_dicts_and_keys():
    lab_dict = {}
    crystal_dict = {}
    data_collection_dict = {}
    data_processing_dict = {}
    dimple_dict = {}
    refinement_dict = {}


    lab_dictionary_keys = ['visit', 'library_plate', 'library_name', 'smiles', 'compound_code', 'protein',
                           'stock_conc', 'expr_conc',
                           'solv_frac', 'soak_vol', 'soak_status', 'cryo_stock_frac', 'cryo_frac',
                           'cryo_transfer_vol', 'cryo_status',
                           'soak_time', 'harvest_status', 'crystal_name', 'mounting_result', 'mounting_time',
                           'data_collection_visit',
                           # 'crystal_id',
                           'file_id']

    crystal_dictionary_keys = ['tag', 'name', 'spacegroup', 'point_group', 'a', 'b', 'c', 'alpha',
                               'beta', 'gamma', 'volume', 'crystal_name',
                               # 'crystal_id',
                               'file_id']

    data_collection_dictionary_keys = ['date', 'outcome', 'wavelength', 'crystal_name', 'crystal_id', 'file_id']

    data_processing_dictionary_keys = ['image_path', 'program', 'spacegroup', 'unit_cell', 'auto_assigned',
                                       'res_overall',
                                       'res_low', 'res_low_inner_shell', 'res_high', 'res_high_15_sigma',
                                       'res_high_outer_shell',
                                       'r_merge_overall', 'r_merge_low', 'r_merge_high', 'isig_overall', 'isig_low',
                                       'isig_high', 'completeness_overall', 'completeness_low', 'completeness_high',
                                       'multiplicity_overall', 'multiplicity_low', 'multiplicity_high',
                                       'cchalf_overall',
                                       'cchalf_low', 'cchalf_high', 'logfile_path', 'mtz_path', 'log_name',
                                       'mtz_name',
                                       'original_directory', 'unique_ref_overall', 'lattice', 'point_group',
                                       'unit_cell_vol',
                                       'alert', 'score', 'status', 'r_cryst', 'r_free', 'dimple_pdb_path',
                                       'dimple_mtz_path',
                                       'dimple_status', 'crystal_name',
                                       # 'crystal_id',
                                       'file_id']

    dimple_dictionary_keys = ['res_high', 'r_free', 'pdb_path', 'mtz_path', 'reference_pdb', 'status', 'pandda_run',
                              'pandda_hit',
                              'pandda_reject', 'pandda_path', 'crystal_name',
                              # 'crystal_id',
                              'file_id']

    refinement_dictionary_keys = ['res', 'res_TL', 'rcryst', 'rcryst_TL', 'r_free', 'rfree_TL', 'spacegroup',
                                  'lig_cc', 'rmsd_bonds',
                                  'rmsd_bonds_TL', 'rmsd_angles', 'rmsd_angles_TL', 'outcome', 'mtz_free', 'cif',
                                  'cif_status', 'cif_prog',
                                  'pdb_latest', 'mtz_latest', 'matrix_weight', 'refinement_path', 'lig_confidence',
                                  'lig_bound_conf', 'bound_conf', 'molprobity_score', 'molprobity_score_TL',
                                  'ramachandran_outliers', 'ramachandran_outliers_TL', 'ramachandran_favoured',
                                  'ramachandran_favoured_TL', 'status', 'crystal_name',
                                  # 'crystal_id',
                                  'file_id']

    dictionaries = [[lab_dict, lab_dictionary_keys], [crystal_dict, crystal_dictionary_keys],
                    [data_collection_dict, data_collection_dictionary_keys],
                    [data_processing_dict, data_processing_dictionary_keys],
                    [dimple_dict, dimple_dictionary_keys], [refinement_dict, refinement_dictionary_keys]]

    return lab_dictionary_keys, crystal_dictionary_keys, data_processing_dictionary_keys, dimple_dictionary_keys, \
           refinement_dictionary_keys, dictionaries, lab_dict, crystal_dict, data_collection_dict, \
           data_processing_dict, dimple_dict, refinement_dict, data_collection_dictionary_keys

# from https://www.ryanbaumann.com/blog/2016/4/30/python-pandas-tosql-only-insert-new-rows
def clean_df_db_dups(df, tablename, engine, dup_cols=[],
                         filter_continuous_col=None, filter_categorical_col=None):
    """
    Remove rows from a dataframe that already exist in a database
    Required:
        df : dataframe to remove duplicate rows from
        engine: SQLAlchemy engine object
        tablename: tablename to check duplicates in
        dup_cols: list or tuple of column names to check for duplicate row values
    Optional:
        filter_continuous_col: the name of the continuous data column for BETWEEEN min/max filter
                               can be either a datetime, int, or float data type
                               useful for restricting the database table size to check
        filter_categorical_col : the name of the categorical data column for Where = value check
                                 Creates an "IN ()" check on the unique values in this column
    Returns
        Unique list of values from dataframe compared to database table
    """
    args = 'SELECT %s FROM %s' %(', '.join(['"{0}"'.format(col) for col in dup_cols]), tablename)
    args_contin_filter, args_cat_filter = None, None
    if filter_continuous_col is not None:
        if df[filter_continuous_col].dtype == 'datetime64[ns]':
            args_contin_filter = """ "%s" BETWEEN Convert(datetime, '%s')
                                          AND Convert(datetime, '%s')""" %(filter_continuous_col,
                              df[filter_continuous_col].min(), df[filter_continuous_col].max())

    if filter_categorical_col is not None:
        args_cat_filter = ' "%s" in(%s)' %(filter_categorical_col,
                          ', '.join(["'{0}'".format(value) for value in df[filter_categorical_col].unique()]))

    if args_contin_filter and args_cat_filter:
        args += ' Where ' + args_contin_filter + ' AND' + args_cat_filter
    elif args_contin_filter:
        args += ' Where ' + args_contin_filter
    elif args_cat_filter:
        args += ' Where ' + args_cat_filter

    df.drop_duplicates(dup_cols, keep='last', inplace=True)
    df = pd.merge(df, pd.read_sql(args, engine), how='left', on=dup_cols, indicator=True)
    df = df[df['_merge'] == 'left_only']
    df.drop(['_merge'], axis=1, inplace=True)
    return df


def transfer_data(database_file):
    def create_list_from_ind(rowno, array, numbers_list, crystal_id, file_id):
        for ind in numbers_list:
            array.append(rowno[ind])
        array.append(crystal_id)
        array.append(file_id)

    def pop_dict(array, dictny, dictionary_keys):
        for i in range(0, len(dictionary_keys)):
            dictny[dictionary_keys[i]].append(array[i])
        return dictny

    def add_keys(dictny, keys):
        for key in keys:
            dictny[key] = []

    lab_dictionary_keys, crystal_dictionary_keys, data_processing_dictionary_keys, dimple_dictionary_keys, \
    refinement_dictionary_keys, dictionaries, lab_dict, crystal_dict, data_collection_dict, \
    data_processing_dict, dimple_dict, refinement_dict, data_collection_dictionary_keys = define_dicts_and_keys()

    # add keys to dictionaries
    for dictionary in dictionaries:
        add_keys(dictionary[0], dictionary[1])

    # numbers relating to where selected in query
    # 17 = number for crystal_name
    lab_table_numbers = list(range(0, 21))

    crystal_table_numbers = list(range(22, 33))
    crystal_table_numbers.insert(len(crystal_table_numbers), 17)

    data_collection_table_numbers = list(range(33, 36))
    data_collection_table_numbers.insert(len(data_collection_table_numbers), 17)

    data_processing_table_numbers = list(range(36, 79))
    data_processing_table_numbers.insert(len(data_processing_table_numbers), 17)

    dimple_table_numbers = list(range(79, 89))
    dimple_table_numbers.insert(len(dimple_table_numbers), 17)

    refinement_table_numbers = list(range(91, 122))
    refinement_table_numbers.insert(len(refinement_table_numbers), 17)

    # connect to master postgres db
    conn = psycopg2.connect('dbname=xchem user=uzw12877 host=localhost')
    c = conn.cursor()
    c.execute('select id from soakdb_files where filename = %s', (database_file,))
    rows = c.fetchall()
    if len(rows) == 1:
        file_id_no = str(rows[0][0])
        print(file_id_no)

    # connect to soakDB
    conn2 = sqlite3.connect(str(database_file))
    c2 = conn2.cursor()

    try:
        # columns with issues: ProjectDirectory, DatePANDDAModelCreated
        for row in soakdb_query(c2):

            try:
                crystal_name = row[17]
            except:
                logging.warning(str('Database file: ' + database_file + ' WARNING: ' + str(sys.exc_info()[1])))
                # temp_protein_cryst_list.append(str(sys.exc_info()[1]))
                return None

            lab_table_list = []
            crystal_table_list = []
            data_collection_table_list = []
            data_processing_table_list = []
            dimple_table_list = []
            refinement_table_list = []

            lists = [lab_table_list, crystal_table_list, data_collection_table_list, data_processing_table_list,
                     dimple_table_list, refinement_table_list]

            numbers = [lab_table_numbers, crystal_table_numbers, data_collection_table_numbers,
                       data_processing_table_numbers, dimple_table_numbers, refinement_table_numbers]
            listref = 0

            for listname in lists:
                create_list_from_ind(row, listname, numbers[listref], crystal_name, file_id_no)
                listref += 1

            # populate query return into dictionary, so that it can be turned into a df and transfered to DB
            pop_dict(lab_table_list, lab_dict, lab_dictionary_keys)
            pop_dict(crystal_table_list, crystal_dict, crystal_dictionary_keys)
            pop_dict(refinement_table_list, refinement_dict, refinement_dictionary_keys)
            pop_dict(dimple_table_list, dimple_dict, dimple_dictionary_keys)
            pop_dict(data_collection_table_list, data_collection_dict,
                     data_collection_dictionary_keys)
            pop_dict(data_processing_table_list, data_processing_dict,
                     data_processing_dictionary_keys)


    except:
        logging.warning(str('Database file: ' + database_file + ' WARNING: ' + str(sys.exc_info()[1])))

        c2.close()
        return None

    # turn dictionaries into dataframes
    labdf = pd.DataFrame.from_dict(lab_dict)
    dataprocdf = pd.DataFrame.from_dict(data_processing_dict)
    refdf = pd.DataFrame.from_dict(refinement_dict)
    dimpledf = pd.DataFrame.from_dict(dimple_dict)


    # start a postgres engine for data transfer
    xchem_engine = create_engine('postgresql://uzw12877@localhost:5432/xchem')
    try:
        # compare dataframes to database rows and remove duplicates
        labdf_nodups = clean_df_db_dups(labdf, 'lab', xchem_engine, lab_dictionary_keys)
        for i in range(0, len(labdf_nodups['expr_conc'])):
            if not type(labdf_nodups['expr_conc'][i]) is int:
                labdf_nodups['expr_conc'][i] = 0
            if not type(labdf_nodups['soak_vol'][i]) is int:
                labdf_nodups['soak_vol'][i] = 0
            if not type(labdf_nodups['solv_frac'][i]) is int:
                labdf_nodups['solv_frac'][i] = 0
            if not type(labdf_nodups['stock_conc'][i]) is int:
                labdf_nodups['stock_conc'][i] = 0

        dataprocdf_nodups = clean_df_db_dups(dataprocdf, 'data_processing', xchem_engine,
                                                          data_processing_dictionary_keys)
        refdf_nodups = clean_df_db_dups(refdf, 'refinement', xchem_engine, refinement_dictionary_keys)
        dimpledf_nodups = clean_df_db_dups(dimpledf, 'dimple', xchem_engine, dimple_dictionary_keys)

        # append new entries to relevant tables
        labdf_nodups.to_sql('lab', xchem_engine, if_exists='append')
        dataprocdf_nodups.to_sql('data_processing', xchem_engine, if_exists='append')
        refdf_nodups.to_sql('refinement', xchem_engine, if_exists='append')
        dimpledf_nodups.to_sql('dimple', xchem_engine, if_exists='append')
    except:
        labdf.to_sql('lab', xchem_engine, if_exists='append')
        dataprocdf.to_sql('data_processing', xchem_engine, if_exists='append')
        refdf.to_sql('refinement', xchem_engine, if_exists='append')
        dimpledf.to_sql('dimple', xchem_engine, if_exists='append')
        c.execute('UPDATE soakdb_files SET status_code = 2 WHERE filename = %s', (database_file,))

    c.execute('UPDATE soakdb_files SET status_code = 2 WHERE filename = %s', (database_file,))


def pop_soakdb(database_file):
    # get proposal number from dls path
    print(database_file)
    try:
        proposal = database_file.split('/')[5].split('-')[0]
    except:
        proposal = 'lb13385'
        print('WARNING: USING DEFAULT PROPOSAL FOR TESTS')
    # get allowed users
    proc = subprocess.Popen(str('getent group ' + str(proposal)), stdout=subprocess.PIPE, shell=True)
    out, err = proc.communicate()
    # get modification date of file
    modification_date = misc_functions.get_mod_date(database_file)
    # add info to soakdbfiles table
    soakdb_entry = models.SoakdbFiles(modification_date=modification_date, filename=database_file, proposal=proposal)
    soakdb_entry.save()

    return out, err, proposal

def pop_proposals(proposal_number):
    # get proposal number from shell
    proc = subprocess.Popen(str('getent group ' + str(proposal_number)), stdout=subprocess.PIPE, shell=True)
    out, err = proc.communicate()
    # create list of fedids (or blank if none found)
    if len(out.decode('ascii'))==0:
        append_list = ''
    else:
        append_list = out.decode('ascii').split(':')[3].replace('\n', '')
    # get soakdbfiles instance where proposal is the same
    soakdb_entry = models.SoakdbFiles.objects.get(proposal=proposal_number)
    # add proposal to proposals table with allowed fedids
    proposal_entry = models.Proposals(proposal=soakdb_entry, fedids=str(append_list))
    proposal_entry.save()

def query_and_list(query, proposals_list, proposal_dict, strucid_list):
    conn, c = connectDB()
    c.execute(query)
    rows = c.fetchall()
    for row in rows:
        try:
            proposal = str(row[0]).split('/')[5].split('-')[0]
        except:
            continue
        if proposal not in proposals_list:
            proposals_list.append(proposal)
            proposal_dict.update({proposal: []})
        else:
            proposal_dict[proposal].append(str(row[1]))

        strucid_list.append(str(row[1]))

    return proposals_list, proposal_dict, strucid_list

def get_strucid_list():

    proposals_list = []
    strucid_list = []
    proposal_dict = {}

    proposals_list, proposal_dict, strucid_list = query_and_list('SELECT bound_conf, strucid FROM proasis_hits',
                                                                 proposals_list, proposal_dict, strucid_list)

    proposals_list, proposal_dict, strucid_list = query_and_list('SELECT reference_pdb, strucid FROM proasis_leads',
                                                                 proposals_list, proposal_dict, strucid_list)

    strucids = list(set(strucid_list))

    return proposal_dict, strucids


def get_fedid_list():
    master_list = []
    conn, c = connectDB()
    c.execute('select fedids from proposals')
    rows = c.fetchall()
    for row in rows:
        if len(row[0]) > 1:
            fedid_list = str(row[0]).split(',')
            for item in fedid_list:
                master_list.append(item)

    final_list = list(set(master_list))
    return final_list

def create_blacklist(fedid, proposal_dict, dir_path):
    search_string=str('%' + fedid + '%')
    proposal_list = []
    all_proposals = list(set(list(proposal_dict.keys())))
    strucid_list = []
    conn, c = connectDB()
    c.execute('select proposal from proposals where fedids like %s', (search_string,))
    rows = c.fetchall()
    for row in rows:
        proposal_list.append(str(row[0]))
    for proposal in proposal_list:
        if proposal in all_proposals:
            all_proposals.remove(proposal)
    for proposal in all_proposals:
        try:
            temp_vals = proposal_dict[proposal]
        except:
            continue
        for item in temp_vals:
            strucid_list.append(item)

    blacklist_file = str(dir_path + '/' + fedid + '.dat')
    with open(blacklist_file, 'wb') as writefile:
        wr = csv.writer(writefile)
        wr.writerow(strucid_list)

def get_pandda_ligand(datafile, pandda_path, crystal):
    conn = sqlite3.connect(datafile)
    c = conn.cursor()
    lig_list = []
    for row in c.execute('''select PANDDA_site_ligand_resname, PANDDA_site_ligand_chain, PANDDA_site_ligand_sequence_number
                  from panddaTable where PANDDAPath like ? and CrystalName like ?''', (pandda_path, crystal)):
        resname = str(row[0])
        chain = str(row[1])
        sequence = str(row[2])
        lig_list.append([resname, chain, sequence])
    return lig_list

def get_pandda_lig_list(bound_conf):
    conn, c = connectDB()
    c.execute('select file_id from refinement where bound_conf like %s', (bound_conf,))
    file_id = str(c.fetchall()[0][0])
    c.execute('select filename from soakdb_files where id = %s', (file_id,))
    datafile = str(c.fetchall()[0][0])
    c.execute('select crystal_name from proasis_hits where bound_conf like %s', (bound_conf,))
    crystal = str(c.fetchall()[0][0])
    c.execute('select pandda_path from dimple where file_id = %s and crystal_name like %s', (file_id, crystal))
    pandda_directory = str(c.fetchall()[0][0])

    lig_list = get_pandda_ligand(datafile,pandda_directory,crystal)

    return lig_list

def check_file_status(filetype, filename, bound_pdb):
    conn, c = connectDB()

    pdb_file_name = str(bound_pdb).split('/')[-1]

    if 'Refine' in str(bound_pdb).replace(pdb_file_name, ''):
        remove_string = str(str(bound_pdb).split('/')[-2] + '/' + pdb_file_name)
        map_directory = str(bound_pdb).replace(remove_string, '')
    else:
        map_directory = str(bound_pdb).replace(pdb_file_name, '')

    exists = column_exists('proasis_hits', str('exists_' + filetype))

    if not exists:
        execute_string = str("ALTER TABLE proasis_hits ADD COLUMN exists_" + filetype + " text;")
        c.execute(execute_string)
        conn.commit()

    execute_string = str("UPDATE proasis_hits SET exists_" + filetype + "=1 where bound_conf like %s")
    if os.path.isfile(str(map_directory + filename)):
        c.execute(execute_string, (bound_pdb,))
        conn.commit()
    else:
        c.execute(execute_string.replace('1','0'), (bound_pdb,))
        conn.commit()

