import psycopg2


def generate_set_values_string(_dict):
    set_list = []
    for k, v in _dict.items():
        set_list.append("{}=\'{}\'".format(k, v))
    return ','.join(set_list)


class DBHelper:
    def __init__(self, config):
        self.conn = psycopg2.connect(
            host=config.get('host'),
            port=config.get('port'),
            database=config.get('database'),
            user=config.get('user'),
            password=config.get('password'),
        )

    def setup(self):
        c = self.conn.cursor()
        try:
            c.execute(project_create_table())
            c.execute(document_create_table())
            c.execute(duma_create_table())
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        c.close()
        self.conn.commit()

    def upsert_project(self, project):
        keys_string = ', '.join(project.keys())
        values_string = ', '.join(f'\'{x}\'' for x in project.values())
        set_string = generate_set_values_string(project)
        statement = 'INSERT INTO project ({}) ' \
                    'VALUES ({}) ' \
                    'ON CONFLICT (internal_id) ' \
                    'DO UPDATE SET {}' \
                    ';'.format(keys_string, values_string, set_string)
        try:
            c = self.conn.cursor()
            c.execute(statement)
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)

    def upsert_documents(self, documents):
        statements = []
        for document in documents:
            keys_string = ', '.join(document.keys())
            values_string = ', '.join(f'\'{x}\'' for x in document.values())
            set_string = generate_set_values_string(document)
            statement = 'INSERT INTO document ({}) ' \
                        'VALUES ({}) ' \
                        'ON CONFLICT (guid) ' \
                        'DO UPDATE SET {}' \
                        ';'.format(keys_string, values_string, set_string)
            statements.append(statement)
        for _ in statements:
            try:
                c = self.conn.cursor()
                c.execute(_)
            except (Exception, psycopg2.DatabaseError) as error:
                print(error)

    def select_statement(self, statement):
        c = self.conn.cursor()
        c.execute(statement)
        result = c.fetchall()
        c.close()
        self.conn.commit()
        return result

    def execute_statement(self, statement):
        c = self.conn.cursor()
        c.execute(statement)
        c.close()
        self.conn.commit()
        
    def get_table_names(self):
        c = self.conn.cursor()
        statement = """SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'orv_reports'"""
        c.execute(statement)
        result = c.fetchall()
        c.close()
        return result
    
    def get_field_names(self, table):
        c = self.conn.cursor()
        statement = f"Select * FROM orv_reports.{table}"
        c.execute(statement)
        c.fetchone()
        result = c.description
        c.close()
        return result


def duma_create_table():
    return """CREATE TABLE IF NOT EXISTS duma (
           duma_project_id TEXT NOT NULL PRIMARY KEY UNIQUE,
           law_title TEXT,
           law_type TEXT,
           status TEXT,
           duma_solution TEXT,
           law_status TEXT,
           review_phase TEXT,
           introduced_by TEXT,
           introduction_date TEXT, 
           document_link TEXT
           );
           """


def project_create_table():
    return """
        CREATE TABLE IF NOT EXISTS project (
        regulation_project_id int4 NOT NULL PRIMARY KEY UNIQUE,
        views_num int4,
        comments_num int4,
        creation_date text,
        publication_date text,
        act_title text,
        developer text,
        okved_list text,
        development_stage text,
        project_status text,
        procedure_type text,
        act_type text,
        regulatory_impact text,
        added_by text,
        responsible text,
        public_discussion_start text,
        public_discussion_end text,
        parallel_stage_discussion_start text,
        parallel_stage_discussion_end text,
        is_regionally_significant bool,
        act_changes_controlling_activities bool,
        is_regulatory_guillotine_applied bool,
        mineco_solution text,
        problem_addressed text,
        act_objectives text,
        persons_affected_by_act text,
        relations_regulated_by_act text,
        act_significance text,
        estimated_effective_date text,
        estimated_transition_period int4,
        departamental_number_if_passed text,
        passing_date_if_passed text,
        registration_number_if_passed text,
        likes_num int4,
        dislikes_num int4,
        last_updated_date text
        );
        """


def document_create_table():
    return """
        CREATE TABLE IF NOT EXISTS document (
        GUID text NOT NULL PRIMARY KEY UNIQUE,
        regulation_project_id int4,
        document_type text, 
        link text, 
        path text,
        last_updated_date text,
        FOREIGN KEY (regulation_project_id) 
        REFERENCES project (regulation_project_id)
        );
        """
