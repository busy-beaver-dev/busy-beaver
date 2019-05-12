import pytest

from busy_beaver.exceptions import EventEmitterException
from busy_beaver.toolbox import EventEmitter


@pytest.fixture
def event_emitter():
    return EventEmitter()


@pytest.fixture
def create_function():
    def _wrapper():
        return "test string"

    return _wrapper


def test_create_event_emitter(event_emitter):
    assert event_emitter is not None


def test_register_function_with_event_emitter(event_emitter, create_function):
    # Arrange
    ee = event_emitter
    ee.on("key1", create_function)

    # Act
    result = ee.emit("key1")

    # Assert
    assert result == "test string"


def test_register_function_with_event_emitter_decorator(event_emitter, create_function):
    # Arrange
    ee = event_emitter

    @ee.on("key1")
    def _wrapper():
        return "decorator"

    # Act
    result = ee.emit("key1")

    # Assert
    assert result == "decorator"


def test_register_same_event_twice_raises_exception(event_emitter, create_function):
    # Arrange
    ee = event_emitter
    ee.on("key1", create_function)

    # Act
    with pytest.raises(EventEmitterException):
        ee.on("key1", create_function)


def test_emit_for_unregistered_event(event_emitter):
    # with pytest.raises(EventEmitterException):
    with pytest.raises(EventEmitterException):
        event_emitter.emit("key1")
