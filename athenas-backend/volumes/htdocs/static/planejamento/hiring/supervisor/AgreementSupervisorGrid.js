Ext._define('planning.hiring.supervisor.AgreementSupervisorGrid', {
    extend: 'planning.hiring.supervisor.SupervisorGrid',

    restWindow: 'planning.hiring.supervisor.AgreementSupervisorWindow',
    controllerName: 'PHAAgreementSupervisor',
});

core.RestfulGrid.register(
    'planning.hiring.supervisor.AgreementSupervisorRestful',
    'planning.hiring.supervisor.AgreementSupervisorGrid'
);
