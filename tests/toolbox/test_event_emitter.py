import pytest

from busy_beaver.exceptions import (
    EventEmitterEventAlreadyRegistered,
    EventEmitterEventNotRegistered,
)
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


def test_event_emitter_with_function_params(event_emitter, create_function):
    # Arrange
    ee = event_emitter

    @ee.on("key1")
    def adder(param1, param2):
        return param1 + param2

    # Act
    result = ee.emit("key1", 2, param2=3)

    # Assert
    assert result == 2 + 3


def test_register_same_event_twice_raises_exception(event_emitter, create_function):
    # Arrange
    ee = event_emitter
    ee.on("key1", create_function)

    # Act
    with pytest.raises(EventEmitterEventAlreadyRegistered):
        ee.on("key1", create_function)


def test_emit_for_unregistered_event(event_emitter):
    with pytest.raises(EventEmitterEventNotRegistered):
        event_emitter.emit("key1")
