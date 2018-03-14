import luigi
import subprocess
import os


class CheckCluster(luigi.Task):
    remote_sub_command = luigi.Parameter(default='ssh -t uzw12877@cs04r-sc-serv-38.diamond.ac.uk')

    def requires(self):
        pass

    def output(self):
        return luigi.LocalTarget('logs/cluster.number')

    def run(self):
        command = ' '.join([
            self.remote_sub_command,
            '"',
            'module load global/cluster >>/dev/null 2>&1; qstat -u uzw12877 | wc -l',
            '"'
            ])
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = process.communicate()
        out = out.decode('ascii')
        if err:
            err = err.decode('ascii')
        print(out)
        if int(out) > 0:
            number = int(out) - 2
        if int(out) == 0:
            number = int(out)
        with self.output().open('wb') as f:
            f.write(str(number))


class SubmitJob(luigi.Task):
    remote_sub_command = luigi.Parameter(default='ssh -t uzw12877@cs04r-sc-serv-38.diamond.ac.uk')
    job_directory = luigi.Parameter()
    job_script = luigi.Parameter()
    max_jobs = luigi.Parameter(default='100')

    def requires(self):
        return CheckCluster()

    def output(self):
        return luigi.LocalTarget(os.path.join(self.job_directory, 'job.id'))

    def run(self):
        with self.input().open('r') as infile:
            number = int(infile.read())

        os.remove(self.input().path)

        if number > int(self.max_jobs):
            raise Exception('Max jobs (' + str(self.max_jobs) + ') exceeded. Please increase max_jobs or wait!')

        os.chdir(self.job_directory)

        submission_string = ' '.join([
            self.remote_sub_command,
            '"',
            'cd',
            self.job_directory,
            '; module load global/cluster >>/dev/null 2>&1; qsub',
            self.job_script,
            '"'
        ])

        print(submission_string)

        submission = subprocess.Popen(submission_string, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = submission.communicate()

        out = out.decode('ascii')
        print('\n')
        print(out)
        print('\n')
        if err:
            err = err.decode('ascii')
            print('\n')
            print(err)
            print('\n')

        job_number = out.split(' ')[2]

        with self.output().open('wb') as f:
            f.write(job_number)


class WriteJob(luigi.Task):
    job_directory = luigi.Parameter()
    job_filename = luigi.Parameter()
    job_name = luigi.Parameter()
    job_executable = luigi.Parameter()
    job_options = luigi.Parameter()

    def requires(self):
        pass

    def output(self):
        return luigi.LocalTarget(os.path.join(self.job_directory, self.job_filename))

    def run(self):
        os.chdir(self.job_directory)
        job_script = '''#!/bin/bash
cd %s
touch %s.running
%s %s > %s.log
rm %s.running
touch %s.done
''' % (self.job_directory, self.job_name, self.job_executable, self.job_options,
       self.job_name, self.job_name, self.job_name)

        with self.output().open('wb') as f:
            f.write(job_script)


class CheckJobOutput(luigi.Task):
    job_directory = luigi.Parameter()
    job_output_file = luigi.Parameter()

    def output(self):
        return luigi.LocalTarget(os.path.join(self.job_directory, str(self.job_output_file + '.done')))

    def run(self):
        if os.path.isfile(os.path.join(self.job_directory, self.job_output_file)):
            with self.output().open('wb') as f:
                f.write('')




