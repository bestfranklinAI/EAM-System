from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
import secrets
import pandas as pd




# class Note(db.Model):
#     id = db.Column(db.Integer, primary_key=True)f
#     data = db.Column(db.String(10000))
#     date = db.Column(db.DateTime(timezone=True), default=func.now())
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    
    
def create_dynamic_table(table_name):
    class DynamicTable(Base):
        __tablename__ = "table_" + secrets.token_hex(4)
    
        id = db.Column(db.Integer, primary_key=True)
        property = db.Column(db.String(100))
        wo_no = db.Column(db.String(20))
        wo_description = db.Column(db.String(200))
        equipment = db.Column(db.String(100))
        equipment_department = db.Column(db.String(50))
        reporter_department = db.Column(db.String(50))
        priority = db.Column(db.String(10))
        status = db.Column(db.String(20))
        fm_type = db.Column(db.String(20))
        service_type = db.Column(db.String(20))
        reporter = db.Column(db.String(100))
        reporter_account = db.Column(db.String(50))
        creation_time = db.Column(db.DateTime)
        work_unit = db.Column(db.String(50))
        principal = db.Column(db.String(100))
        completion_time = db.Column(db.DateTime)
        actual_total_working_hours = db.Column(db.Float)
        operation = db.Column(db.String(100))

    db.create_all()
    tables[table_name] = DynamicTable
    return DynamicTable



#create a dictionary for easy access to the tables
tables = {'User' : User}

#custom function to insert data into the table
def insert_data_into_table(table_name, df):
    for index, row in df.iterrows():
        record = tables[table_name](
            property=row['項目 Property'],
            wo_no=row['編號 WO No.'],
            wo_Description=row['工單描述 Wo Description'],
            equipment=row['設施設備 Equipment'],
            equipment_department=row['設備所屬部門 Equipment Department'],
            reporter_department=row['報單人部門 Reporter Department'],
            priority=row['逼切性 Priority'],
            status=row['狀態 Status'],
            fm_type=row['業務類型 FM type'],
            service_Type=row['服務類型 Service Type'],
            reporter=row['報單人 Repoter'],
            reporter_account=row['報單人賬號 Reporter'],
            creation_time=row['報單時間 Creation Time'],
            work_unit=row['工作組 Work Unit'],
            principal=row['責任人 Principal'],
            completion_time=row['工單完成時間 Completion Time'],
            actual_total_working_hours=row['實際縂工時 Actual Total Working Hours'],
            operation=row['操作 Operation']
        )
        db.session.add(record)
    db.session.commit()


#retrieve whole table
def retrieve_data_from_table(table_name):
    query_result = tables[table_name].query.all()
    df_retrieved = pd.DataFrame([(record.property, record.wo_no, record.wo_description, record.equipment, record.equipment_department, record.reporter_department, record.priority, record.status, record.fm_type, record.service_type, record.reporter, record.reporter_account, record.creation_time, record.work_unit, record.principal, record.completion_time, record.actual_total_working_hours, record.operation) for record in query_result], columns=['項目 Property', '編號 WO No.', '工單描述 Wo Description', '設施設備 Equipment', '設備所屬部門 Equipment Department', '報單人部門 Reporter Department', '逼切性 Priority', '狀態 Status', '業務類型 FM type', '服務類型 Service Type', '報單人 Reporter', '報單人賬號 Reporter','報單時間 Creation Time','工作組 Work Unit', '責任人 Principal', '工單完成時間 Completion Time', '實際縂工時 Actual Total Working Hours', '操作 Operation'])
    return df_retrieved
