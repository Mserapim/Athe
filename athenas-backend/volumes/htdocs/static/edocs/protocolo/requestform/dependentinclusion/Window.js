Ext._define('edocs.protocolo.requestform.dependentinclusion.Window', {
    extend: 'edocs.protocolo.box.ComposeWindow',

    mixins: { '1': 'edocs.protocolo.requestform.mixins.Common' },

    _resource: 'RequestFormDependentInclusion',

    rest: 'edocs.protocolo.requestform.dependentinclusion.Restful',

    width: 900,

    getFormPanel: function (cfg) {
        if (!this._formPanel) {
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                items: [
                    this.getMainPanel(),
                    {
                        layout: 'vbox',
                        border: false,
                        height: 450,
                        items: [
                            this.getDependentPanel(cfg),
                            this.getAttachmentPanel()
                        ]
                    }
                ]
            });
        }

        return this._formPanel;
    },

    getMainPanel: function (cfg) {
        if (!this._mainPanel) {
            this._mainPanel = Ext._create('Ext.Panel', {
                frame: true,
                layout: 'form',
                items: [
                    this.getCodeField(cfg),
                    {
                        xtype: 'container',
                        layout: 'hbox',
                        items: [
                            {
                                xtype: 'container',
                                layout: 'form',
                                flex: 2.75,
                                items: this.getHomeCourtField(cfg)
                            },
                            {
                                xtype: 'container',
                                layout: 'form',
                                flex: 1.25,
                                labelWidth: 50,
                                items: this.getDocumentTypeField('REQUERIMENTO')  // mixin
                            }
                        ]
                    },
                    this.getSubjectField(cfg, {
                        value: 'Requerimento Inclusão de Dependentes',
                        readOnly: true,
                    }),
                    this.getControlContainer(cfg),
                    this.getContactNumberField(cfg),
                ]
            });
        }

        return this._mainPanel;
    },

    getDependentPanel: function (cfg) {
        if (!this._dependentPanel) {
            this._dependentPanel = Ext._create('edocs.protocolo.requestform.dependent.Grid', {
                title: 'Dependentes a serem incluídos',
                flex: 1,
                gridAutoLoad: false,
                columnAction: false
            });
        }

        return this._dependentPanel;
    },

    observeMovement: function () {
        edocs.protocolo.requestform.dependentinclusion.Window.superclass.observeMovement.call(this, {});

        var value = this.movement();
        var grid = this.getDependentPanel();

        if (value) {
            var protocol = this.values ? this.values.protocol : this.protocol;

            grid.enable();
            grid.setParam('dependent_inclusion', protocol);
            grid.setFilterProperty('dependent_inclusion__pk', protocol, 100);
        } else {
            grid.disable();
            grid.setParam('dependent_inclusion', undefined);
            grid.setFilterProperty('dependent_inclusion__pk', undefined, 100, false);
            grid.getStore().removeAll();
        }
    }
});

edocs.protocolo.box.MainGrid.registerSpecialType({
    title: 'Requerimento Inclusão de Dependentes',
    iconCls: '',
    restWindow: 'edocs.protocolo.requestform.dependentinclusion.Window',
    specialType: 'dependentinclusion',
    group: 'Dependentes'
});
