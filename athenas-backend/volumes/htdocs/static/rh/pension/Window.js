Ext._define('rh.pension.Window', {
    extend: 'core.RestfulWindow',
    rest: 'rh.pension.Restful',
    width: 550,

    getEventsPanel: function(cfg) {
        if(!this._eventsPanel)
            this._eventsPanel = Ext._create('core.fields.RelatedRestfulField', {
                frame: true,
                border: false,
                title: "Eventos",
                name: 'events',
                relatedname: 'pension_events',
                width: 540,
                height: 370,
                rest: this.rest,
                sourceRest: 'rh.gfp.payroll.EventRestful',
                oId: cfg.oId,
            });

        return this._eventsPanel;
    },

    getEventPanel: function(cfg) {
        if(!this._eventPanel)
            this._eventPanel = Ext._create('Ext.Panel', {
                frame: true,
                border: false,
                defaults: {
                    width: 400
                },
                title: 'Geral',
                layout: 'form',
                items: [
                    {
                        xtype: 'choicefield',
                        fieldLabel: 'Tipo de pensão',
                        name: 'type_of_pension',
                        hiddenName: 'type_of_pension',
                        choiceId: 'pensao.TYPE_OF_PENSION',
                        width: 215
                    },
                    {
                        xtype: 'rest-autocompletefield',
                        fieldLabel: 'Servidor',
                        name: 'servidor',
                        displayField: 'unicode',
                        allowBlank: false,
                        rest: 'rh.employee.Restful'
                    },
                    {
                        xtype: 'rest-autocompletefield',
                        fieldLabel: 'Pensionista',
                        name: 'pensionista',
                        displayField: 'unicode',
                        allowBlank: false,
                        rest: 'rh.person.naturalperson.Restful'
                    },
                    {
                        xtype: 'rest-autocompletefield',
                        fieldLabel: 'Representante legal',
                        name: 'representante_legal',
                        displayField: 'unicode',
                        allowBlank: true,
                        rest: 'rh.person.naturalperson.Restful'
                    },
                    {
                        xtype: 'choicefield',
                        fieldLabel: 'Tipo de cálculo',
                        name: 'tipo',
                        hiddenName: 'tipo',
                        choiceId: 'pensao.TYPE_OF_CALC',
                        width: 215
                    },
                    {
                        xtype: 'numberfield',
                        fieldLabel: 'Valor',
                        name: 'valor',
                        decimalPrecision: 6
                    },
                    {
                        xtype: 'rest-autocompletefield',
                        fieldLabel: 'Evento Servidor',
                        name: 'event_employee',
                        displayField: 'unicode',
                        allowBlank: false,
                        rest: 'rh.gfp.payroll.EventRestful'
                    },
                    {
                        xtype: 'rest-autocompletefield',
                        fieldLabel: 'Evento Servidor 13º',
                        name: 'event_employee_13',
                        displayField: 'unicode',
                        allowBlank: true,
                        rest: 'rh.gfp.payroll.EventRestful'
                    },
                    {
                        xtype: 'rest-autocompletefield',
                        fieldLabel: 'Evento Pensionista',
                        name: 'event_pensioner',
                        displayField: 'unicode',
                        allowBlank: false,
                        rest: 'rh.gfp.payroll.EventRestful'
                    },
                    {
                        xtype: 'datefield',
                        fieldLabel: 'Data início',
                        name: 'data_inicio',
                        format: 'd/m/Y'
                    },
                    {
                        xtype: 'datefield',
                        fieldLabel: 'Data fim',
                        name: 'data_fim',
                        format: 'd/m/Y',
                        blank: true
                    },
                    {
                        xtype: 'rest-autocompletefield',
                        fieldLabel: 'Publicação',
                        name: 'publicacao',
                        displayField: 'unicode',
                        allowBlank: true,
                        rest: 'rh.publicacao.Restful'
                    },

                ]
            });

        return this._eventPanel;
    },

    _observe: function() {

        var grid_events = this.getEventsPanel();
        if(this.oId) {
            grid_events.enable();
        }else{
            grid_events.disable();
        }
    },

    getTabPanel: function(cfg) {
        if(!this._tabPanel)
            this._tabPanel = Ext._create('Ext.TabPanel', {
                height: 450,
                border: false,
                activeTab: 0,
                deferredRender: false,
                items: [
                    this.getEventPanel(cfg),
                    this.getEventsPanel(cfg),
                ]
            });

        return this._tabPanel;
    },

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                items: this.getTabPanel(cfg),
                submit_all_checks: true
            });

        return this._formPanel;
    },

    constructor: function(cfg) {
        rh.pension.Window.superclass.constructor.call(this, cfg);
        this._observe();
    }
});
