Ext._define('corregedoria.prontuary.individualperformance.listindication.Window', {
    extend: 'core.RestfulWindow',

    rest: 'corregedoria.prontuary.individualperformance.listindication.Restful',

    width: 630,

    getAttachmentsGrid: function(cfg) {
        if(!this._attachmentsGrid) {
            this._attachmentsGrid = Ext._create('corregedoria.prontuary.individualperformance.listindication.attachments.Grid', {
                region: 'center',
                layout: 'form',
                title: 'Anexos',
                border: true,
                height: 300,
                disabled: true,
                gridAutoLoad: true,
                columnAction: false,
                hideItemsToolbar:['edit', 'download', '-', 'search'],
            });
        }
        return this._attachmentsGrid;
    },

    observer: function() {
        if (this.oId) {
            this.getAttachmentsGrid().enable();
            this.getAttachmentsGrid().params = {detaillistindication: this.oId,};
        } else {
            this.getAttachmentsGrid().disable();
        }
        this.getAttachmentsGrid().setFilterProperty('detaillistindication_id', this.oId, 100);
    },

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                labelWidth: 110,
                items: [
                    {
                        xtype:'panel',
                        autoHeight:true,
                        layout: 'column',
                        items: [
                            {
                                xtype:'panel',
                                autoHeight:true,
                                labelWidth: 35,
                                layout: 'form',
                                columnWidth: 0.45,
                                items: [
                                    {
                                        xtype: 'textfield',
                                        fieldLabel: 'Edital',
                                        name: 'edital',
                                        width: 220,

                                    }
                                ]
                            },
                            {
                                xtype:'panel',
                                autoHeight:true,
                                labelWidth: 45,
                                layout: 'form',
                                columnWidth: 0.3,
                                items: [
                                    {
                                        xtype: 'choicefield',
                                        fieldLabel: 'Tipo',
                                        hiddenName: 'criteria',
                                        width: 120,
                                        choiceId: 'prontuary.CRITERIA',
                                    },
                                ]
                            },
                            {
                                xtype:'panel',
                                autoHeight:true,
                                labelWidth: 30,
                                layout: 'form',
                                columnWidth: 0.25,
                                items: [
                                    {
                                        xtype: 'datefield',
                                        fieldLabel: 'Data',
                                        width: 110,
                                        name: 'date_edital',
                                    },
                                ]
                            },
                        ]
                    },
                    {
                        xtype:'panel',
                        autoHeight:true,
                        layout: 'form',
                        labelWidth: 90,
                        style: {
                            marginLeft: '402px',
                        },
                        items: [
                            {
                                xtype: 'combo',
                                id: 'list_figuration',
                                hiddenName: 'list_figuration',
                                fieldLabel: 'Figurou em lista',
                                width: 100,
                                editable: false,
                                triggerAction: 'all',
                                store: [
                                    [1, ''],
                                    [2, 'SIM'],
                                    [3, 'NÃO'],
                                ],
                            },
                        ]
                    },
                    this.getAttachmentsGrid(cfg),
                ]
            });

        return this._formPanel;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});
        Ext.applyIf(cfg, {
            disableSaveAndNew: true,
            saveAndContinue: {
                scope: this,
                fn: function(instance) {
                    this.getFormPanel().getForm().setValues(instance);
                    this.oId = instance.pk;
                    this.action = 'update';
                    this.observer();
                }
            }
        });
        corregedoria.prontuary.individualperformance.listindication.Window.superclass.constructor.call(this, cfg);
        this.observer();
    },

});
