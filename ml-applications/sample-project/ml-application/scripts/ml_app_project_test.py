from ml_app_project import MlApplicationProject
from ml_app_res import MlApplicationResource
from ml_app_impl_res import MlApplicationImplResource
from ml_app_instance_res import MlApplicationInstanceResource

class TestMlApplicationProject:
    _project: MlApplicationProject

    def __init__(self, env_name: str):
        self._project = MlApplicationProject(env_name)

    def deployApp(self) -> 'TestMlAppImpl':
        self.deploy()

    def cleanup(self) -> None:
        self._project.undeploy(True)


class TestMlAppImpl:

    def __init__(self):
        pass

    def instantiate(self) -> 'TestMlAppInstance':
        MlApplicationResource.




class TestMlAppInstance:

    def trigger(self) -> 'TestMlAppInstance':
        pass

    def predict(self) -> 'TestMlAppInstance':
        pass

    def cleanup(self) -> 'TestMlAppInstance':
        pass

    def checkExecution(self) -> 'TestMlAppInstance':
        pass


MlApplicationTest
testProject: MlApplicationProjectTest = MlApplicationProjectTest()
instance: TestMlAppInstance = testProject.deploy().instantiate()
instance.trigger("abc").checkExecution().predict()
instance.trigger("abc").checkExecution().predict().assertPredction()


