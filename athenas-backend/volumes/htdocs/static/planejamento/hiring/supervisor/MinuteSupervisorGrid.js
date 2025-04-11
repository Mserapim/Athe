Ext._define('planning.hiring.supervisor.MinuteSupervisorGrid', {
    extend: 'planning.hiring.supervisor.SupervisorGrid',

    restWindow: 'planning.hiring.supervisor.MinuteSupervisorWindow',
    controllerName: 'PHMMinuteSupervisor',
});

core.RestfulGrid.register(
    'planning.hiring.supervisor.MinuteSupervisorRestful',
    'planning.hiring.supervisor.MinuteSupervisorGrid'
);
