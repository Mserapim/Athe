

Ext._define('rh.hoursworkcontract.WindowGridInterval', {
    extend: 'Ext.Window',

    width: 700,
    height: 400,

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});
        Ext.applyIf(
            cfg,
            {
                closable: true,
                values: {},
            }
        );
        Ext.apply(
            cfg,
            {
                border: false,
                layout: 'fit',
                items: [
                    this.getFormPanel(cfg)
                ],
            }
        );

        rh.hoursworkcontract.WindowGridInterval.superclass.constructor.call(this, cfg);
        this._observe();
    },

    _observe: function(){
        if(this.values.hours_work_contract){
            this.getWorkHourIntervalGrid().setParam('hours_work_contract', this.values.hours_work_contract);
            this.getWorkHourIntervalGrid().setFilterProperty('hours_work_contract', this.values.hours_work_contract);
        }else
            this.getWorkHourIntervalGrid().setFilterProperty('hours_work_contract', 0, 1001, false);
    },

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                items: [
                    this.getWorkHourIntervalGrid(cfg, {hours_work_contract: cfg.values.hours_work_contract})
                ]
            });
        return this._formPanel;
    },

    getWorkHourIntervalGrid: function(cfg_window, cfg) {
        if(!this._workHourInterval)
            this._workHourInterval = Ext._create('rh.workhourinterval.Grid', {
                title: 'Intervalos de Horário de Trabalho',
                hours_work_contract: cfg.hours_work_contract,
                region: 'center',
                border: false,
                width: 670,
                height: 360,
            });
        return this._workHourInterval;
    },
});