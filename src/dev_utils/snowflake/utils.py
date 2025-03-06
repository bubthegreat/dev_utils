import logging
import snowflake.connector


LOGGER = logging.getLogger(__name__)

class SnowRunner:
    def __init__(self, user, account, password, warehouse, role=None):
        LOGGER.info("Setting up new connection for user %s", user)
        self._user = user
        self._account = account
        self._password = password
        self.warehouse = warehouse
        self._ctx = None
        self.version = self.get_version()
        self.set_warehouse(self.warehouse)
        if role is not None:
            self.use_role(role)
            
    def use_role(self, role):
        sql_command = f"USE ROLE {role};"
        result = self.execute(sql_command)
        LOGGER.info("Set role to %s", role)
        return result

    def set_warehouse(self, warehouse):
        self._warehouse = warehouse
        result = self.execute(f"USE WAREHOUSE {self.warehouse};")
        LOGGER.info("Warehouse set to %s", self.warehouse)
        return result
    
    def use_database(self, database):
        result = self.execute(f"USE DATABASE {database};")
        LOGGER.info("Set DATABASE to %s", database)
        return result

    @property
    def ctx(self):
        if self._ctx and not self._ctx.is_closed():
            return self._ctx
        
        LOGGER.info("No context object yet - getting new context for queries.")
        self._ctx = snowflake.connector.connect(
            user=self._user, account=self._account, password=self._password
        )
        LOGGER.info("New context successfully created.")
        return self._ctx

    def execute(self, sql):
        """Run a query with a context managed snowflake connector."""
        # LOGGER.debug("Running sql: %s", sql)
        cursor = self.ctx.cursor()
        cursor.execute(sql)
        result = cursor.fetchall()
        return result


    def get_version(self):
        """Get the snowflake current version."""
        query_results = self.execute("SELECT current_version()")
        first_result = query_results[0]
        version = first_result[0]
        return version
