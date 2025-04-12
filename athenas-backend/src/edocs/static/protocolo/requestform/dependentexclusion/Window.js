Ext._define('edocs.protocolo.requestform.dependentexclusion.Window', {
    extend: 'edocs.protocolo.box.ComposeWindow',

    mixins: { '1': 'edocs.protocolo.requestform.mixins.Common' },

    _resource: 'RequestFormDependentExclusion',

    rest: 'edocs.protocolo.requestform.dependentexclusion.Restful',

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
                            this.getDependentExclusionItemPanel(cfg),
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
                                items: this.getHomeCourtField(cfg),
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
                        value: 'Requerimento Exclusão de Dependentes',
                        readOnly: true,
                    }),
                    this.getControlContainer(cfg),
                    this.getContactNumberField(cfg),
                ]
            });
        }

        return this._mainPanel;
    },

    getDependentExclusionItemPanel: function (cfg) {
        if (!this._dependentExclusionItemPanel)
            this._dependentExclusionItemPanel = Ext._create('edocs.protocolo.requestform.dependentexclusionitem.Grid', {
                title: 'Dependentes a serem excluídos',
                flex: 1,
                gridAutoLoad: false,
                columnAction: false
            });

        return this._dependentExclusionItemPanel;
    },

    observeMovement: function () {
        edocs.protocolo.requestform.dependentexclusion.Window.superclass.observeMovement.call(this, {});

        var value = this.movement();
        var grid = this.getDependentExclusionItemPanel();

        if (value) {
            var protocol = this.values ? this.values.protocol : this.protocol;

            grid.enable();
            grid.setParam('dependent_exclusion', protocol);
            grid.setFilterProperty('dependent_exclusion__pk', protocol, 100);
        } else {
            grid.disable();
            grid.setParam('dependent_exclusion', undefined);
            grid.setFilterProperty('dependent_exclusion__pk', undefined, 100, false);
            grid.getStore().removeAll();
        }
    }
});

edocs.protocolo.box.MainGrid.registerSpecialType({
    title: 'Requerimento Exclusão de Dependentes',
    iconCls: '',
    restWindow: 'edocs.protocolo.requestform.dependentexclusion.Window',
    specialType: 'dependentexclusion',
    group: 'Dependentes',
});
