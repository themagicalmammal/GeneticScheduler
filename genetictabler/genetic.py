from random import choice, choices, randint

course_count = 0
slot_count = 0
day_count = 0
class_count = 0
course_bits = 0
slot_bits = 0
class_bits = 0
total_slots = 0
course_quota = []
teacher_quota = []
repeat_quota = []
tables = []


def initialize_genotype(no_courses, classes, slots, days, daily_rep, teachers):
    """
    The initialize_genotype() initializes and stores important data relevant to
    the user defined timetable(s)'s design in global variables so that they
    can be easily used multiple times throughout the program as per requirement.
    """

    global course_count
    global slot_count
    global day_count
    global class_count
    global course_bits
    global total_slots
    global slot_bits
    global class_bits
    global repeat_quota
    global teacher_quota

    course_count = no_courses
    slot_count = slots
    day_count = days
    class_count = classes

    total_slots = slot_count * day_count
    course_bits = len(bin(course_count)) - 2
    slot_bits = len(bin(total_slots)) - 2
    class_bits = len(bin(course_count)) - 2
    """
    Course_bits, slot_bits and class bits are the lengths of binary string needed to
    represent them respectively. For example if course_count is 8, then the maximum course
    number will be 8 which requires 4 bits, hence course_bits will be equal to 4.
    """

    calc_course_quota()

    if isinstance(daily_rep, int):
        repeat_quota = [daily_rep for _ in range(course_count)]
    elif isinstance(daily_rep[0], int) and len(daily_rep) == course_count:
        repeat_quota = daily_rep
    else:
        raise ValueError("Invalid data supplied for daily repetitions.")

    repeat_quota = [repeat_quota[:] for _ in range(class_count)]

    if isinstance(teachers, int):
        teacher_quota = [teachers] * course_count
    elif isinstance(teachers[0], int) and len(teachers) == course_count:
        teacher_quota = teachers
    else:
        raise ValueError("Invalid data supplied for teachers.")

    return [course_bits, slot_bits, slot_count * day_count * class_count]


def calc_course_quota():
    """
    This function calculates an array course_quota which stores the maximum allowed
    occurrence of a course/subject/module in a week/scheduled number of days.
    """

    global course_quota

    q_max = total_slots // course_count
    if total_slots % course_count == 0:
        course_quota = [q_max for _ in range(course_count)]
    else:
        course_quota = [(q_max + 1) for _ in range(course_count)]

        extra_slots = (q_max + 1) * course_count - total_slots

        n = randint(1, course_count - extra_slots)
        for i in range(extra_slots):
            course_quota[n + i] -= 1

    course_quota = [course_quota[:] for _ in range(class_count)]


def encode_class():
    """
    The encode_class() function generates random binary strings whose
    integer values represent a course/module/subject
    """
    class_code = bin(randint(1, class_count))[2:]

    """
    Left padding of random binary strings with 0 is done to ensure each string
    is of same consistent length.
    """
    class_code = "0" * (class_bits - len(class_code)) + class_code
    return class_code


def encode_slot():
    """
    The encode_slot() function generates random binary strings whose integer
    values represent slot number for a day.
    """

    slot_code = bin(randint(1, total_slots))[2:]
    slot_code = "0" * (slot_bits - len(slot_code)) + slot_code
    return slot_code


def encode_course():
    """
    The encode_slot() function generates random binary strings whose integer
    values represents a course/module/subject.
    """
    course_code = bin(randint(1, course_count))[2:]
    course_code = "0" * (course_bits - len(course_code)) + course_code
    return course_code


def generate_gene():
    course_code = encode_course()
    class_code = encode_class()
    slot_code = encode_slot()

    return course_code + slot_code + class_code


def extract_slot_day(gene):
    """
    The class_slot is a cumulative class slot number, we calculate day number
    and slot number for that day for a gene using this class_slot number.
    """
    class_slot = int(gene[course_bits:course_bits + slot_bits], 2)
    slot_no = class_slot % slot_count
    day_no = class_slot // slot_count

    if slot_no == 0:
        slot_no = slot_count
        day_no -= 1

    return slot_no, day_no


def calculate_fitness(gene):
    """
    This function determines fitness_score of a gene(course schedule) by checking few things:-
    1)   If there already exists a course schedule for the same slot of the same or different class,
        fitness_score of the gene is decreased.
    2)   If the same course is scheduled for any of the adjacent slots in the same class,
        fitness_score of that gene is reduced.
    3)   If a course is occurring more han a fixed number of times, the fitness_score of
        that gene is reduced.
    """
    fitness_score = 100
    course = int(gene[0:course_bits], 2)

    slot_no, day_no = extract_slot_day(gene)
    class_no = int(gene[course_bits + slot_bits:], 2)

    if tables[class_no - 1][day_no - 1][slot_no - 1] != 0:
        fitness_score *= 0.01

    for i in range(class_count):
        if tables[i][day_no - 1][slot_no - 1] == course:
            fitness_score *= 0.6

    if slot_no != 1 and tables[class_no - 1][day_no - 1][slot_no -
                                                         2] == course:
        fitness_score *= 0.6

    if slot_no != slot_count and tables[class_no - 1][day_no -
                                                      1][slot_no] == course:
        fitness_score *= 0.6

    if course_quota[class_no - 1][course - 1] < 1:
        fitness_score *= 0.01

    if tables[class_no - 1][day_no - 1].count(course) >= 2:
        fitness_score *= 0.01

    if (tables[class_no - 1][day_no - 1].count(course) >=
            repeat_quota[class_no - 1][course - 1]):
        fitness_score *= 0.5

    temp_counter = 0
    for i in range(class_count):
        if tables[i][day_no - 1][slot_no - 1] == course:
            temp_counter += 1
    if temp_counter == teacher_quota[course - 1]:
        fitness_score *= 0.01
    return fitness_score


def generate_table_skeleton():
    """
    This function returns a 3d array with 0 value for all positions.
    We use this array to store the schedules and the timetables.
    """
    global tables

    for _ in range(class_count):
        class_table = []
        for _ in range(day_count):
            day = [0 for _ in range(slot_count)]
            class_table.append(day)
        tables.append(class_table)
    return tables


def fit_slot(gene):
    """
    The fit_slot() function fills the tables array with fit course schedules that
    are returned by run_evolution().
    """

    global tables
    global course_quota
    global repeat_quota
    global teacher_quota

    course = int(gene[0:course_bits], 2)

    slot_no, day_no = extract_slot_day(gene)
    class_no = int(gene[course_bits + slot_bits:], 2)

    # Python list indexing starts from 0, hence we subtract 1 from class_no, day_no,
    # slot_no which are natural numbers.
    tables[class_no - 1][day_no - 1][slot_no - 1] = course
    course_quota[class_no - 1][course - 1] -= 1


def generate_population(size):
    """
    our population will be a list of genes
    """
    return [generate_gene() for _ in range(size)]


def single_point_crossover(gene_a, gene_b):
    """
    For crossover, we randomly choose one out of course_code, slot_code and class_code
    to swap between the genes.
    """
    c = choice([1, 2, 3])

    if c == 1:
        gene_c = gene_b[0:course_bits] + gene_a[course_bits:]
        gene_d = gene_a[0:course_bits] + gene_b[course_bits:]

    elif c == 2:
        gene_c = (gene_a[:course_bits] +
                  gene_b[course_bits:course_bits + slot_bits] +
                  gene_a[course_bits + slot_bits:])
        gene_d = (gene_b[:course_bits] +
                  gene_a[course_bits:course_bits + slot_bits] +
                  gene_b[course_bits + slot_bits:])

    else:
        gene_c = (gene_a[:course_bits + slot_bits] +
                  gene_b[course_bits + slot_bits:])
        gene_d = (gene_b[:course_bits + slot_bits] +
                  gene_a[course_bits + slot_bits:])
    return [gene_c, gene_d]


def multi_point_crossover(gene_a, gene_b, points):
    """
    We use the single point crossover, multiple times
    """
    for _ in range(points):
        gene_a, gene_b = single_point_crossover(gene_a, gene_b)

    return [gene_a, gene_b]


def mutation(gene, course_bit_length, slot_bit_length):
    """
    For mutation, we randomly choose any one of course_code, slot_code or class_code and
    replace it with another random code of its type.
    """
    c = choice([1, 2, 3])

    if c == 1:
        random_course = encode_course()
        mutated_gene = random_course + gene[course_bit_length:]

    elif c == 2:
        random_slot = encode_slot()
        mutated_gene = (gene[:course_bit_length] + random_slot +
                        gene[course_bit_length + slot_bit_length:])
    else:
        random_class = encode_class()
        mutated_gene = gene[:course_bit_length +
                            slot_bit_length] + random_class

    return mutated_gene


def selection_pair(population):
    return choices(
        population=population,
        weights=[calculate_fitness(gene) for gene in population],
        k=2,
    )


def sort_population(population):
    return sorted(population, key=calculate_fitness, reverse=True)


def run_evolution(
    course_bit_length,
    slot_bit_length,
    population_size,
    max_fitness,
    max_generations,
):
    population = generate_population(population_size)
    for i in range(max_generations):
        population = sorted(population, key=calculate_fitness, reverse=True)

        if calculate_fitness(population[0]) >= max_fitness:
            return population[0]

        next_generation = population[0:2]

        for _ in range(len(population) // 2 - 1):
            parents = selection_pair(population)
            children = single_point_crossover(parents[0], parents[1])
            child_a = mutation(children[0], course_bit_length, slot_bit_length)
            child_b = mutation(children[1], course_bit_length, slot_bit_length)
            next_generation += [child_a, child_b]

        population = next_generation
    return population[0]


def generate_timetable(classes=6, courses=4, slots=6, days=5, repeat=2, teachers=1,
                       population_size=40, max_fitness=100, max_generations=50,):

    course_bit_length, slot_bit_length, all_slots = \
        initialize_genotype(courses, classes, slots, days, repeat, teachers)
    generate_table_skeleton()
    while all_slots > 0:
        gene = run_evolution(
            course_bit_length,
            slot_bit_length,
            population_size,
            max_fitness,
            max_generations,
        )
        if gene != 0:
            fit_slot(gene)
            all_slots -= 1
    return tables
