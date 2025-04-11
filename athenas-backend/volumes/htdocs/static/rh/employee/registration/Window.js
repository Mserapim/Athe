Ext._define('rh.employee.registration.Window', {
    extend: 'core.RestfulWindow',

    rest: 'rh.employee.registration.Restful',

    width: 1400,

    getFormPanel: function() {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                frame: true,
                border: false,
                items: [
                    this.getNaturalPersonDataFormPanel(
                        {},
                        {
                            employeePk: '',
                            employeeRegistry: '',
                            naturalPersonPk: '',
                        }
                    ),
                ],

            });

        return this._formPanel;
    },

    getNaturalPersonDataFormPanel: function(cfgPanel, cfg) {
        cfg = core.nullValue(cfg, {});
        Ext.apply(cfg, {title: '',});
        if(!this._naturalPersonDataFormPanel){
            this._naturalPersonDataFormPanel = Ext._create('rh.employee.specialized.tab.NaturalPersonDataFormPanel', cfg);
        }
        return this._naturalPersonDataFormPanel;
    },
});