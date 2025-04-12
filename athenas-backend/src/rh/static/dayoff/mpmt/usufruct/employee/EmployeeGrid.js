Ext._define('rh.dayoff.mpmt.usufruct.employee.EmployeeGrid', {
    extend: 'rh.dayoff.mpmt.usufruct.Grid',

    restWindow: 'rh.dayoff.mpmt.usufruct.employee.EmployeeWindow',

    getGroupFilterAction: function () {
        if (!this._groupFilter)
            this._groupFilter = Ext._create('rh.dayoff.mpmt.acquisitionperiod.GroupFilterAction', { objToFilter: this, propertyName: 'activity__acquisition_period__group_period' });
        return this._groupFilter;
    },

    getConfigurationFilterAction: function () {
        if (!this._configurationFilter)
            this._configurationFilter = Ext._create('rh.dayoff.mpmt.acquisitionperiod.ConfigurationFilterAction', { objToFilter: this, propertyName: 'activity__acquisition_period__configuration_period__configuration' });
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

        rh.dayoff.mpmt.usufruct.employee.EmployeeGrid.superclass.constructor.call(this, cfg);
    }
});

core.RestfulGrid.register(
    'rh.dayoff.mpmt.usufruct.employee.EmployeeRestful',
    'rh.dayoff.mpmt.usufruct.employee.EmployeeGrid'
);
