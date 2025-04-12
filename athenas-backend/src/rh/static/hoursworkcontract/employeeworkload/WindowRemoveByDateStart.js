Ext._define('rh.hoursworkcontract.employeeworkload.WindowRemoveByDateStart', {
    extend: 'Ext.Window',

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});
        Ext.applyIf(cfg, {title: 'Aplicar Escala'});
        Ext.apply(
            cfg,
            {
                width: 500,
                height: 190,
                resizable: false,
                border: false,
                frame: true,
                modal: true,
                items: [
                    this.getFormPanel()
                ]
            }
        );
        rh.hoursworkcontract.employeeworkload.WindowRemoveByDateStart.superclass.constructor.call(this, cfg);
        this._observe();
    },

    _observe: function(){
        if(this._workhourContract){
            this.getHoursField().setValue(this._workhourContract);
            this.getHoursField().setReadOnly(true);
        }else
            this.getHoursField().setReadOnly(false);
    },

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                height: 160,
                frame: true,
                items: [
                    this.getFieldSetPeriod(),
                ],
                buttons: [{
                    text: 'Aplicar',
                    scope: this,
                    handler: function() {
                        this.removeByDateStart(this.getFormPanel().getForm().getValues());
                    }
                }]
            });
        return this._formPanel;
    },

    getFieldSetPeriod: function(cfg){
        if(!this.fieldSetPeriod){
            cfg = core.nullValue(cfg, {});
            Ext.applyIf(
                cfg,
                {
                    title: 'Remover escalas que começam na data',
                    collapsible: false,
                    collapsed: false,
                    labelAlign: 'left',
                    items:[
                        this.getHoursField(),
                        {
                            allowBlank: false,
                            fieldLabel: 'In\u00edcio',
                            name: 'date_start',
                            xtype: 'datefield',
                        },
                        // {
                        //     allowBlank: true,
                        //     fieldLabel: 'Fim',
                        //     name: 'date_end',
                        //     xtype: 'datefield',
                        // },
                    ],
                    scope: this,
                }
            );
            this.fieldSetPeriod = Ext._create('Ext.form.FieldSet', cfg);
        }
        return this.fieldSetPeriod;
    },

    getHoursField: function(cfg_window, cfg){
        if(!this._hoursField){
            cfg = core.nullValue(cfg, {});
            Ext.apply(
                cfg,
                {
                    xtype: 'rest-autocompletefield',
                    fieldLabel: 'Escala',
                    allowBlank: false,
                    rest: 'rh.hoursworkcontract.workload.Restful',
                    name: 'hours_work_contract_workload'
                }
            );
            this._hoursField = Ext._create('core.fields.AutocompleteField', cfg);
        }
        return this._hoursField;
    },

    removeByDateStart: function(params){
        var rest = Ext._create('rh.hoursworkcontract.employeeworkload.Restful', {});
        var mask = new Ext.LoadMask(this.getEl(), {msg: 'Processando informações.'});
        var wnd = this;

        mask.show();
        rest.removeByDateStart(
            params,
            {
                scope: this,
                fn: function(rst) {
                    core.invokeCallback((wnd.externalCallback || {fn: Ext.emptyFn}), rst.message);
                    wnd.close();
                }
            },
            {
                fn: function(message) {
                    Ext.Msg.show({
                        title: 'Informando',
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK,
                        msg: message
                    });
                }
            },
            {
                fn: function() {
                    mask.hide();
                }
            }
        );
    },
});

