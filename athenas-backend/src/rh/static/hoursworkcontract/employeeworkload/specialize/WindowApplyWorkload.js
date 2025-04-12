Ext._define('rh.hoursworkcontract.employeeworkload.specialize.WindowApplyWorkload', {
    extend: 'Ext.Window',

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                title: 'Aplicar Escala'
            }
        );

        Ext.apply(
            cfg,
            {
                width: 500,
                height: 420,
                resizable: false,
                border: false,
                frame: true,
                modal: true,
                items: [
                    this.getFormPanel()
                ]
            }
        );

        rh.hoursworkcontract.employeeworkload.specialize.WindowApplyWorkload.superclass.constructor.call(this, cfg);

        this._observe();
    },

    _observe: function(){
        if(this._workhourContract){
            this.getHoursDestinyField().setValue(this._workhourContract);
        }
    },

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                height: 390,
                frame: true,
                items: [
                    this.getFieldSetEmployee(),
                    this.getFieldSetPeriod(),
                    this.getFieldSetSource(),
                    {
                        xtype: 'checkbox',
                        boxLabel: 'Reiniciar Origem após Fim de Vigência do Destino',
                        allowBlank: true,
                        name: 'reapply'
                    },
                ],
                buttons: [{
                    text: 'Aplicar',
                    scope: this,
                    handler: function() {
                        this._apply(this.getFormPanel().getForm().getValues());
                    }
                }]
            });
        return this._formPanel;
    },

    getFieldSetEmployee: function(cfg){
        if(!this.fieldSetEmployee){
            cfg = core.nullValue(cfg, {});
            Ext.applyIf(
                cfg,
                {
                    title: 'Opções para filtro de Servidor',
                    collapsible: false,
                    collapsed: false,
                    labelAlign: 'left',
                    items:[
                        {
                            xtype: 'rest-autocompletefield',
                            fieldLabel: 'Localidade',
                            allowBlank: true,
                            rest: 'rh.localidade.Restful',
                            name: 'locality',
                        },
                        {
                            xtype: 'rest-autocompletefield',
                            fieldLabel: 'Departamento',
                            allowBlank: true,
                            rest: 'rh.workplace.Restful',
                            name: 'workplace',
                        },
                        {
                            xtype: 'checkbox',
                            boxLabel: 'Ignorar outras opções e escolher TODOS Servidores?',
                            allowBlank: true,
                            name: 'allEmployee'
                        }
                    ],
                    scope: this,
                }
            );
            this.fieldSetEmployee = Ext._create('Ext.form.FieldSet', cfg);
        }
        return this.fieldSetEmployee;
    },

    getFieldSetPeriod: function(cfg){
        if(!this.fieldSetPeriod){
            cfg = core.nullValue(cfg, {});
            Ext.applyIf(
                cfg,
                {
                    title: 'Período de Vigência',
                    collapsible: false,
                    collapsed: false,
                    labelAlign: 'left',
                    items:[
                        {
                            allowBlank: false,
                            fieldLabel: 'In\u00edcio',
                            name: 'date_start',
                            xtype: 'datefield',
                        },
                        {
                            allowBlank: true,
                            fieldLabel: 'Fim',
                            name: 'date_end',
                            xtype: 'datefield',
                        },
                    ],
                    scope: this,
                }
            );
            this.fieldSetPeriod = Ext._create('Ext.form.FieldSet', cfg);
        }
        return this.fieldSetPeriod;
    },

    getFieldSetSource: function(cfg){
        if(!this.fieldSetSource){
            cfg = core.nullValue(cfg, {});
            Ext.applyIf(
                cfg,
                {
                    title: 'Escala de Origem e Destino',
                    collapsible: false,
                    collapsed: false,
                    labelAlign: 'left',
                    items:[
                        this.getHoursOriginField(),
                        this.getHoursDestinyField(),
                    ],
                    scope: this,
                }
            );
            this.fieldSetSource = Ext._create('Ext.form.FieldSet', cfg);
        }
        return this.fieldSetSource;
    },

    _apply: function(params){
        this.applyEmployeeWorkplace(params);
    },

    applyEmployeeWorkplace: function(params){
        var rest = Ext._create('rh.hoursworkcontract.employeeworkload.specialize.Restful', {});
        var mask = new Ext.LoadMask(this.getEl(), {msg: 'Processando informações.'});
        var wnd = this;

        mask.show();
        rest.applyEmployeeWorkplace(
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

    getHoursOriginField: function(cfg_window, cfg){
        if(!this._hoursOriginField){
            cfg = core.nullValue(cfg, {});
            Ext.apply(
                cfg,
                {
                    xtype: 'rest-autocompletefield',
                    fieldLabel: 'Origem',
                    allowBlank: true,
                    rest: 'rh.hoursworkcontract.workload.Restful',
                    name: 'hoursworkcontractworkload_origin'
                }
            );
            this._hoursOriginField = Ext._create('core.fields.AutocompleteField', cfg);
        }
        return this._hoursOriginField;
    },

    getHoursDestinyField: function(cfg_window, cfg){
        if(!this._hoursDestinyField){
            cfg = core.nullValue(cfg, {});
            Ext.apply(
                cfg,
                {
                    xtype: 'rest-autocompletefield',
                    fieldLabel: 'Destino',
                    allowBlank: true,
                    rest: 'rh.hoursworkcontract.workload.Restful',
                    name: 'hoursworkcontractworkload_destiny'
                }
            );
            this._hoursDestinyField = Ext._create('core.fields.AutocompleteField', cfg);
        }
        return this._hoursDestinyField;
    },
});

