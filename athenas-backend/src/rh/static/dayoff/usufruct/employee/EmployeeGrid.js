Ext._define('rh.dayoff.usufruct.employee.EmployeeGrid', {
    extend: 'rh.dayoff.usufruct.Grid',

    restWindow: 'rh.dayoff.usufruct.employee.EmployeeWindow',

    getGroupFilterAction: function () {
        if (!this._groupFilter)
            this._groupFilter = Ext._create('rh.dayoff.acquisitionperiod.GroupFilterAction', { objToFilter: this, propertyName: 'activity__acquisition_period__group_period' });
        return this._groupFilter;
    },

    getConfigurationFilterAction: function () {
        if (!this._configurationFilter)
            this._configurationFilter = Ext._create('rh.dayoff.acquisitionperiod.ConfigurationFilterAction', { objToFilter: this, propertyName: 'activity__acquisition_period__configuration_period__configuration' });
        return this._configurationFilter;
    },

    constructor: function (cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.apply(
            cfg,
            {
                configOrderToolBar: ['groupFilter'],
            }
        );

        rh.dayoff.usufruct.employee.EmployeeGrid.superclass.constructor.call(this, cfg);
    }
});

core.RestfulGrid.register(
    'rh.dayoff.usufruct.employee.EmployeeRestful',
    'rh.dayoff.usufruct.employee.EmployeeGrid'
);
