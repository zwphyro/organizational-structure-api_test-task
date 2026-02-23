import pytest
from unittest.mock import AsyncMock, Mock

from src.department.exceptions import DuplicateDepartmentNameError
from src.department.models import Department
from src.department.service import DepartmentService
from src.exceptions import NotFoundError


@pytest.fixture
def department_repository():
    department_repository_mock = AsyncMock()

    department_repository_mock.get_by_id = AsyncMock()
    department_repository_mock.add = Mock()
    department_repository_mock.get_children = AsyncMock()
    department_repository_mock.check_is_child = AsyncMock()
    department_repository_mock.delete = AsyncMock()
    department_repository_mock.reassign_parent = AsyncMock()

    return department_repository_mock


@pytest.fixture
def employee_repository():
    employee_repository_mock = AsyncMock()

    employee_repository_mock.add = Mock()
    employee_repository_mock.reassign_department = AsyncMock()

    return employee_repository_mock


@pytest.fixture
def uow(department_repository, employee_repository):
    uow_mock = AsyncMock()

    uow_mock.departments = department_repository
    uow_mock.employees = employee_repository
    uow_mock.commit = AsyncMock()
    uow_mock.flush = AsyncMock()
    uow_mock.rollback = AsyncMock()
    uow_mock.close = AsyncMock()

    return uow_mock


@pytest.fixture
def department_service(uow):
    return DepartmentService(uow)


@pytest.mark.asyncio
async def test_create_department_ok(department_service):
    department = await department_service.create_department("Test name", None)

    assert department.name == "Test name"
    assert department.parent_id is None
    assert department_service.uow.departments.add.call_count == 1
    assert department_service.uow.departments.add.call_args[0][0] == department


@pytest.mark.asyncio
async def test_create_department_parent_not_none_ok(department_service):
    parent_department = Department(id=1, children=[])
    department_service.uow.departments.get_by_id = AsyncMock(
        return_value=parent_department
    )

    department = await department_service.create_department("Test name", 1)

    assert department.name == "Test name"
    assert department.parent_id == 1
    assert department_service.uow.departments.add.call_count == 1
    assert department_service.uow.departments.add.call_args[0][0] == department


@pytest.mark.asyncio
async def test_create_department_parent_not_none_not_found(department_service):
    department_service.uow.departments.get_by_id = AsyncMock(return_value=None)

    with pytest.raises(NotFoundError):
        await department_service.create_department("Test name", 1)


@pytest.mark.asyncio
async def test_create_department_name_exists(department_service):
    parent_department = Department(id=1, children=[Department(name="Test name")])
    department_service.uow.departments.get_by_id = AsyncMock(
        return_value=parent_department
    )

    department_service.uow.departments.check_is_child = AsyncMock(return_value=True)

    with pytest.raises(DuplicateDepartmentNameError):
        await department_service.create_department("Test name", 1)


@pytest.mark.asyncio
async def test_create_employee_ok(department_service):
    department = Department(id=1, employees=[])
    department_service.uow.departments.get_by_id = AsyncMock(return_value=department)

    employee = await department_service.create_employee(1, "John Doe", "Engineer", None)

    assert employee.department_id == 1
    assert employee.full_name == "John Doe"
    assert employee.position == "Engineer"
    assert employee.hired_at is None
    assert department_service.uow.employees.add.call_count == 1
    assert department_service.uow.employees.add.call_args[0][0] == employee


@pytest.mark.asyncio
async def test_create_employee_department_not_found(department_service):
    department_service.uow.departments.get_by_id = AsyncMock(return_value=None)

    with pytest.raises(NotFoundError):
        await department_service.create_employee(1, "John Doe", "Engineer", None)


@pytest.mark.asyncio
async def test_get_department_ok(department_service):
    department_service.uow.departments.get_by_id = AsyncMock(
        return_value=Department(id=1, name="Test name", employees=[])
    )
    department_service.uow.departments.get_children = AsyncMock(return_value=[])

    department, employees, children = await department_service.get_department(
        1, 1, True
    )

    assert department.id == 1
    assert department.name == "Test name"
    assert employees == []
    assert children == []
    assert department_service.uow.departments.get_by_id.call_count == 1
    assert department_service.uow.departments.get_by_id.call_args[0][0] == 1
    assert department_service.uow.departments.get_by_id.call_args[1][
        "include_employees"
    ]
    assert department_service.uow.departments.get_children.call_count == 1
    assert department_service.uow.departments.get_children.call_args[0][0] == 1
    assert department_service.uow.departments.get_children.call_args[1]["depth"] == 1


@pytest.mark.asyncio
async def test_get_department_no_employees_ok(department_service):
    department_service.uow.departments.get_by_id = AsyncMock(
        return_value=Department(id=1, name="Test name", employees=[])
    )
    department_service.uow.departments.get_children = AsyncMock(return_value=[])

    department, employees, children = await department_service.get_department(
        1, 1, False
    )

    assert department.id == 1
    assert department.name == "Test name"
    assert employees is None
    assert children == []
    assert department_service.uow.departments.get_by_id.call_count == 1
    assert department_service.uow.departments.get_by_id.call_args[0][0] == 1
    assert not department_service.uow.departments.get_by_id.call_args[1][
        "include_employees"
    ]
    assert department_service.uow.departments.get_children.call_count == 1
    assert department_service.uow.departments.get_children.call_args[0][0] == 1
    assert department_service.uow.departments.get_children.call_args[1]["depth"] == 1


@pytest.mark.asyncio
async def test_get_department_not_found(department_service):
    department_service.uow.departments.get_by_id = AsyncMock(return_value=None)

    with pytest.raises(NotFoundError):
        await department_service.get_department(1, 1, True)


@pytest.mark.asyncio
async def test_move_department_ok(department_service):
    department_service.uow.departments.get_by_id = AsyncMock(
        return_value=Department(id=1, name="Test name", parent_id=None)
    )
    department_service.uow.departments.move = AsyncMock()

    department = await department_service.move_department(1, {"name": "New name"})

    assert department.name == "New name"
    assert department_service.uow.departments.get_by_id.call_count == 1
    assert department_service.uow.departments.get_by_id.call_args[0][0] == 1


@pytest.mark.asyncio
async def test_delete_department_ok(department_service):
    department_service.uow.departments.get_by_id = AsyncMock(
        return_value=Department(id=1, name="Test name", parent_id=None)
    )
    department_service.uow.departments.delete = AsyncMock()

    await department_service.delete_department(1, None)

    assert department_service.uow.departments.get_by_id.call_count == 1
    assert department_service.uow.departments.get_by_id.call_args[0][0] == 1


@pytest.mark.asyncio
async def test_delete_department_reassign_ok(department_service):
    async def get_by_id_mock(id: int, **_):
        if id == 1:
            return Department(id=1, name="Test name", parent_id=None)
        elif id == 2:
            return Department(id=2, name="Test name", parent_id=1)

    department_service.uow.departments.get_by_id = get_by_id_mock
    department_service.uow.departments.check_is_child = AsyncMock(return_value=False)

    await department_service.delete_department(1, 2)
    assert department_service.uow.departments.check_is_child.call_count == 1
    assert department_service.uow.departments.check_is_child.call_args[0][0] == 1
    assert department_service.uow.departments.check_is_child.call_args[0][1] == 2
