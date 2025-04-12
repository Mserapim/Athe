
Ext._define('judicial.parts.AdditionalDiligenceWindow', {
    extend: 'judicial.PartLawsuitWindow',

    rest: 'judicial.parts.AdditionalDiligenceRestful',

    width: 800,
    // autoCreate: true,

    readDataCallback: function(instance) {
        this.additionalDiligence(instance.pk);
    },

    getMainPanel: function () {
        if (!this._mainPanel)
            this._mainPanel = Ext._create('Ext.Panel', {
                title: 'Diligências',
                layout: 'form',
                border: false,
                frame: true,
                items: [
                    {
                        fieldLabel: "Título",
                        name: "dispatch_title",
                        xtype: "textfield",
                        allowBlank: true,
                        width: 650,
                    },
                    this.getInvestigationGrid()
                ]
            });
        return this._mainPanel;
    },

    getInvestigationGrid: function() {
        if(!this._investigationGrid) {
            this._investigationGrid = Ext._create('judicial.diligences.ExecutionOrganGrid', {
                title: 'Diligências',
                height: 500,
                configOrderToolBar: ['add', 'edit', 'remove', '-', 'assumeDelivery', '-', '->'],
                gridAutoLoad: false,
            });

            this._investigationGrid.addEvents('afterCopyDiligence');
            this._investigationGrid.addEvents('afterFinishDiligence');

            this._investigationGrid.on({
                scope: this,
                afterCopyDiligence: function() {
                    this.close();
                    this.callback.success.scope.getStore().reload();
                },
                afterFinishDiligence: function() {
                    this.close();
                    this.callback.success.scope.getStore().reload();
                }
            });
        }

        return this._investigationGrid;
    },

    additionalDiligence: function(value, dispatch) {
        dispatch = (dispatch === undefined ? true : dispatch);
        if(value !== undefined) {
            this._additionalDiligence = value;
            if(dispatch)
                this.observerAdditionalDiligence();
        }

        return this._additionalDiligence;
    },


    observerAdditionalDiligence: function() {
        var value = this.additionalDiligence();

        if(value) {
            this.getInvestigationGrid().enable();
            this.getInvestigationGrid().setParam('part', value);
            this.getInvestigationGrid().setFilterProperty('part', value, 101);
        }
        else {
            this.getInvestigationGrid().disable();
            this.getInvestigationGrid().setParam('part', 0);
            this.getInvestigationGrid().setFilterProperty('part', 0, 101);
            this.getInvestigationGrid().getStore().removeAll();
        }

    },

    getRightButtons: function(cfg) {
        if(!this._rightButtons)
            this._rightButtons = [
                {
                    text: 'Salvar',
                    scope: this,
                    handler: function () { this.save(true); }
                },
                {
                    text: 'Fechar',
                    scope: this,
                    handler: function () { this.close(); }
                }
        ];

        return this._rightButtons;
    },

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                items: [
                    {
                        xtype: 'tabpanel',
                        activeTab: 0,
                        height: 580,
                        border: false,
                        items: [
                            this.getMainPanel()
                        ]
                    }
                ]
            });

        return this._formPanel;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});
        Ext.applyIf(
            cfg,
            {
                buttonAlign: 'left',
                disableSaveAndNew: true,
                saveAndContinue: {
                    scope: this,
                    fn: function(instance) {
                        this.oId = instance.pk;
                        this.additionalDiligence(instance.pk);
                        this.action = 'update';
                    }
                },
                border: false,
                title: 'Diligencias Adicionais'
            });

        judicial.parts.AdditionalDiligenceWindow.superclass.constructor.call(this, cfg);
        this.observerAdditionalDiligence();

        this.addEvents('afterCopy');

        this.on({
            scope: this,
            show: function() {
                if(this.action === "create")
                    this.save(true);
            }
        });
    }
});

judicial.PartLawsuitGrid.register('judicial.additionaldiligence', 'judicial.parts.AdditionalDiligenceWindow');
