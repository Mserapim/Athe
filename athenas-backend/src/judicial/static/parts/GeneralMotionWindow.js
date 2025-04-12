Ext._define('judicial.parts.GeneralMotionWindow', {
    extend: 'judicial.PartLawsuitWindow',

    rest: 'judicial.parts.GeneralMotionRestful',

    width: 900,

    getContentPanel: function(cfg) {
        if(!this._contentTabPanel)
            this._contentTabPanel = Ext._create('Ext.Panel', {
                title: 'Conteúdo',
                border: false,
                items: [
                    {
                        layout: 'form',
                        border: false,
                        frame: true,
                        items: [
                            {
                                allowBlank: false,
                                fieldLabel: "Título",
                                name: "name",
                                xtype: "textfield",
                                width: 740
                            },
                            this.getLegalMovementField(cfg),
                        ]
                    },
                    {
                        xtype: 'container',
                        border: false,
                        items: [
                            {
                                allowBlank: false,
                                height: 450,
                                name: "content",
                                xtype: "ckeditor"
                            }
                        ]
                    }
                ]
            });

        return this._contentTabPanel;
    },

     getLegalMovementField: function(cfg) {
        if(!this._legalMovimentField){
            this._legalMovimentField = Ext._create('core.fields.AutocompleteField', {
                xtype: "rest-autocompletefield",
                fieldLabel: "Movimento",
                allowBlank: false,
                rest: "judicial.taxonomy.LegalMovimentRestful",
                name: "legal_classification",
                disabled: false,
                gridConfig: {
                    columnAction: false,
                    allowUpdate: false,
                    allowRemove: false,
                    listeners:{
                        render: function(grid){
                            var tbar = grid.getToolbar();
                            tbar.remove(tbar.getComponent(0)); //novo
                            tbar.remove(tbar.getComponent(0)); // editar
                            tbar.remove(tbar.getComponent(0)); // remover
                        }
                    }
                },
                preFilter: [
                    {
                        property: 'judicial_classification',
                        value: true,
                        stage: 101
                    },
                    {
                        property: 'children__isnull',
                        value: false,
                        stage: -102
                    }
                ],
            });
        }
        return this._legalMovimentField;
    },


    getScientifyWorkplaceGrid: function(cfg) {
        if(!this._scientifyWorkplaceGrid)
            this._scientifyWorkplaceGrid = Ext._create('judicial.ScientifyWorkplaceGrid', {
                title: 'Comunicações',
                gridAutoLoad: false,
                columnAction: false
            });

        return this._scientifyWorkplaceGrid;
    },

    getAttachementPanel: function(cfg) {
        if(!this._attachmentPanel)
            this._attachmentPanel = Ext._create('judicial.parts.AttachedGrid', {
                title: 'Anexos',
                gridAutoLoad: false
            });

        return this._attachmentPanel;
    },

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: false,
                items: [
                    {
                        xtype: 'tabpanel',
                        activeTab: 0,
                        height: 610,
                        items: [
                            this.getContentPanel(cfg),
                            this.getAttachementPanel(cfg),
                            this.getScientifyWorkplaceGrid(cfg)
                        ]
                    }
                ]
            });

        return this._formPanel;
    },

    generalMotionInstance: function(value, dispatch) {
        dispatch = (dispatch === undefined ? true : dispatch);

        if(value !== undefined) {
            this._generalMotionInstance = value;

            if(dispatch) this.observerGeneralMotion();
        }

        return this._generalMotionInstance;
    },

    observerGeneralMotion: function() {
        var value = this.generalMotionInstance();

        if(value) {
            this.getAttachementPanel().enable();
            this.getAttachementPanel().setParam('attached_document', value);
            this.getAttachementPanel().setFilterProperty('attached_document', value, 1000);

            this.getScientifyWorkplaceGrid().enable();
            this.getScientifyWorkplaceGrid().setParam('part', value);
            this.getScientifyWorkplaceGrid().setFilterProperty('part', value, 1001);
        }
        else {
            this.getAttachementPanel().disable();
            this.getAttachementPanel().setParam('attached_document', value);
            this.getAttachementPanel().setFilterProperty('attached_document', 0, 1000);
            this.getAttachementPanel().getStore().removeAll();

            this.getScientifyWorkplaceGrid().disable();
            this.getScientifyWorkplaceGrid().setParam('part', 0);
            this.getScientifyWorkplaceGrid().setFilterProperty('part', 0, 1001, false);
            this.getScientifyWorkplaceGrid().getStore().removeAll();
        }
    },

    readDataCallback: function(instance) {
        this.generalMotionInstance(instance.pk);
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(cfg, {
            buttonAlign: 'left',
            disableSaveAndNew: true,
            saveAndContinue: {
                scope: this,
                fn: function(instance) {
                    this.oId = instance.pk;
                    this.action = 'update';

                    this.readDataCallback(instance);
                }
            }
        });

        judicial.parts.GeneralMotionWindow.superclass.constructor.call(this, cfg);
        this.observerGeneralMotion();
    }
});

judicial.PartLawsuitGrid.register('judicial.generalmotion', 'judicial.parts.GeneralMotionWindow');
