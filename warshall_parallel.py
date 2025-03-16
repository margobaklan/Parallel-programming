from Pyro4 import expose
import time
import random


class Solver:
    def __init__(self, workers=None, input_file_name=None, output_file_name=None):
        self.workers = workers
        self.input_file_name = input_file_name
        self.output_file_name = output_file_name
        print("Initialized")

    def solve(self):
        print("Job Started")
        n = self.read_input()
        graph = self.get_random_graph(n)

        rows_per_worker = self.split_rows_among_workers(n)
        current_row = 0
        start_time = time.time()

        mapped_results = []
        for i in range(len(self.workers)):
            if rows_per_worker[i] == 0:
                continue
            sub_rows = graph[current_row:current_row + rows_per_worker[i]]
            mapped_results.append(
                self.workers[i].floyd_worker(sub_rows, graph)  
            )
            current_row += rows_per_worker[i]

        result = self.myreduce(mapped_results)
        total_time = time.time() - start_time
        self.write_output(result, total_time, n)

    @staticmethod
    @expose
    def myreduce(mapped_results):
        print("Reducing results")
        output = []
        for result in mapped_results:
            result = result.value  
            output.append(result)
        print("Reduce completed")
        return output

    @staticmethod
    @expose
    def floyd_worker(sub_rows, full_graph):
        n = len(full_graph)
        for k in range(n):  
            k_row = full_graph[k]  
            for i in range(len(sub_rows)):
                for j in range(n):
                    sub_rows[i][j] = min(sub_rows[i][j], sub_rows[i][k] + k_row[j])
        return sub_rows

    @staticmethod
    def get_random_graph(n, value_range=(1, 10), inf=9999):
        graph = [[(random.randint(*value_range) if i != j else 0) for j in range(n)] for i in range(n)]
        return graph
    
    def split_rows_among_workers(self, n):
        num_workers = len(self.workers)
        rows_per_worker = [n // num_workers] * num_workers
        extra_rows = n % num_workers
        for i in range(extra_rows):
            rows_per_worker[i] += 1
        return rows_per_worker

    def read_input(self):
        with open(self.input_file_name, 'r') as f:
            n = int(f.readline().strip())
        return n

    def write_output(self, dist, total_time, n):
        with open(self.output_file_name, 'w') as f:
            f.write("\nParallel mode\n")
            f.write("Graph size: {}\n".format(n))
            f.write("Total computation time:" + str(total_time) + "seconds\n")
            for row in dist:
                f.write(' '.join(map(str, row)) + '\n')
        print("Output written to", self.output_file_name)
