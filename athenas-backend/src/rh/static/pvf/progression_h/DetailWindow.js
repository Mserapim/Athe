Ext._define('rh.pvf.progression_h.DetailWindow', {

    rest: 'rh.pvf.progression_h.Restful',
    extend:'rh.pvf.portalrequest.DetailWindow',

    height: 760,

    getTabPanel: function (cfg) {
        if (!this._tabPanel)
            this._tabPanel = Ext._create('Ext.TabPanel', {
                tabPanelHeight: 650,
                height: 680,
                border: false,
                activeTab: 0,
                deferredRender: false,
                items: [
                    this.getManagerPanel(cfg),
                ]
            });

        return this._tabPanel;
    },

    getManagerPanel: function (cfg) {
        if (!this._managementPanel)
            this._managementPanel = Ext._create('Ext.Panel', {
                frame: true,
                border: false,
                title: 'Principal',
                layout: 'form',
                items: [
                    {
                        xtype: 'fieldset',
                        title: 'Informações:',
                        layout: 'column',
                        border: true,
                        items: [
                            {
                                columnWidth: .2,
                                xtype: 'displayfield',
                                style: {fontSize: '12px'},
                                value: 'Data da solicitação: ',
                            },
                            {
                                columnWidth: cfg.data.acquisitive_period?.3:.8,
                                xtype: 'displayfield',
                                fieldLabel: 'Data da solicitação:',
                                style: {fontSize: '12px',marginBottom: '12px'},
                                value: Ext.util.Format.date(cfg.data.date, 'd/m/Y')
                            },
                            {
                                columnWidth: .2,
                                xtype: 'displayfield',
                                style: {fontSize: '12px'},
                                value: 'Tipo: ',
                            },
                            {
                                columnWidth: .8,
                                fieldLabel: 'Tipo',
                                style: {fontSize: '12px',marginBottom: '12px'},
                                xtype: 'displayfield',
                                value:cfg.data.type_of_request
                            },
                            {
                                columnWidth: .2,
                                xtype: 'displayfield',
                                style: {fontSize: '12px'},
                                value: 'Solicitante: ',
                            },
                            {
                                columnWidth: .8,
                                fieldLabel: 'Solicitante',
                                style: {fontSize: '12px',marginBottom: '12px'},
                                xtype: 'displayfield',
                                value: cfg.data.employee_unicode
                            },
                            {
                                columnWidth: .2,
                                xtype: 'displayfield',
                                style: {fontSize: '12px'},
                                hidden:cfg.data.custom_approver_current?false:true,
                                value: 'Aprovador Atual: ',
                            },
                            {
                                fieldLabel: 'Aprovador Atual',
                                xtype: 'displayfield',
                                columnWidth: .8,
                                style: {fontSize: '12px',marginBottom: '12px'},
                                hidden:cfg.data.custom_approver_current?false:true,
                                value:cfg.data.custom_approver_current
                            },
                            {
                                columnWidth: .2,
                                xtype: 'displayfield',
                                style: {fontSize: '12px'},
                                value: 'Situação: ',
                            },
                            {
                                fieldLabel: 'Situação',
                                xtype: 'displayfield',
                                columnWidth: .8,
                                style: {fontSize: '12px',marginBottom: '12px'},
                                value:cfg.data.status_display
                            },
                        ]
                    },
                    this.getFieldSet(cfg),
                    this.getTabHistory(cfg),
                    
                ]
            });
        return this._managementPanel;
    },

    getFieldSet:function(cfg){
        _fieldsSet = [
            this.getDocumentFieldSet(cfg),
        ]
        return _fieldsSet;
    },

    getDocumentFieldSet: function (cfg) {
        if (!this._document)
            this._document = Ext._create('Ext.form.FieldSet', {
                title: 'Documentos',
                items: [
                    this.getDocumentGrid(cfg),
                ]
            });

        return this._document;
    },

    getDocumentGrid: function(cfg) {
        if(!this._documentGrid) {
            this._documentGrid = Ext._create('rh.pvf.progression_h.document.Grid',{
                hideItemsToolbar: [],
                columnAction: false,
                region: 'center',
                height: 130,
                border: false,
                scope: this,
                //doubleClickHandler: function () { },
                configOrderToolBar: [],
            });
        }
        this._documentGrid.setFilterProperty('pr_progression_h', cfg.data.pk)
        return this._documentGrid;
    },

    getApproverButtons: function(cfg) {
        if(!this._buttons) {
            this._buttons = [];
            if (cfg.data.approver_request){
                this._buttons.push(        
                    new Ext._create('Ext.Button', {
                        text: 'Indeferir',
                        iconCls: true,
                        height:28,
                        with:32,
                        hidden:cfg.data.buttons == 'effective_point'?false:true,
                        scope: this,
                        icon: '/' + global.Context + '/static/rh/images/pasu_nao_autorizado.png',
                        handler: function() {  this.rejectRequest(cfg)}
                            
                    }),            
                    new Ext._create('Ext.Button', {
                        text: 'Devolver ao Solicitante',
                        scope: this,
                        height:28,
                        with:32,
                        hidden:cfg.data.buttons == 'effective_point'?false:true,
                        iconCls: true,
                        icon: '/' + global.Context + '/static/rh/images/athenas-0197.png',
                        handler: function() { this.returnApplicant(cfg)}
                    }),
                    new Ext._create('Ext.Button', {
                        text: 'Efetivar',
                        hidden:cfg.data.buttons == 'effective_point'?false:true,
                        scope: this,
                        height:28,
                        with:32,
                        iconCls: true,
                        icon: '/' + global.Context + '/static/rh/images/pasu_autorizado.png',
                        handler: function() { this.effectiveRequest(cfg) }
                    })
                    
                )
            }               
        
        }
        
        return this._buttons;
    },

});