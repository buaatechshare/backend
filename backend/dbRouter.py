import random

class PrimaryReplicaRouter:
    def db_for_read(self,model,**hints):
        """
        数据库读操作，随机分配至主/从数据库
        """
        return random.choice(['default','rep1'])

    def db_for_write(self,model,**hints):
        """
        数据库写操作，只在default数据库(mysql-primary)上进行
        """
        return 'default'

    def allow_relation(self,obj1,obj2,**hints):
        """
        对象间关系约束
        """
        # db_list = ('primary','rep1')
        # if obj1._state.db in db_list and obj2._state.db in db_list:
        #     return True
        # return None
        return True

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        return True