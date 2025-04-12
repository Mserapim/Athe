/**
 *
 **/
 Ext._define('rh.cnmp.FormationManage', {
    extend: 'toolkit.widget.TabPanel',

    getInformationMember: function() {
        if(!this._informationmember){
            this._informationmember = Ext._create('rh.employee.Grid', {
                region: 'center',
                minHeight: 200,
                // hideColumns: ['ativo', ],
                hideItemsToolbar: ['add', 'edit', 'remove', ],
                hideActions: ['add', 'edit', 'remove', 'copy', ],
            });
        }

        this._informationmember.getSelectionModel().on({
            scope: this,
            'rowselect': function(sm, index, record) {
                this.setInformationMember(record.data.pk);
            },
            'rowdeselect': function(sm) {
                this.setInformationMember(null);
            }
        });

        this._informationmember.getStore().on({
            scope: this,
            'load': function() {
                this.setInformationMember(null);
            }
        });

        this._informationmember.getStore().on({
            scope: this,
            'load': function() {
                var selected = (this._informationmember.getSelectionModel().getSelected());

                if(selected)
                    this.setInformationMember(selected.get('pk'));
                else
                    this.setInformationMember(null);
            }
        });

        this._informationmember.setFilterProperty('tipo', 'M');
        this._informationmember.setParam('tipo', 'M');

        return this._informationmember;
    },

    getGraduation: function() {
        if(!this._teaching) {
            this._teaching = Ext._create('rh.cnmp.GraduationCNMPGrid', {
                title: 'Graduação',
            });

        }

        return this._teaching;
    },

    getImprovementAndGraduate: function() {
        if(!this._address) {
            this._address = Ext._create('rh.cnmp.ImprovementAndGraduateCNMPGrid', {
                title: 'Aperfeiçoamento e Pós-Graduação',
            });
        }
        return this._address;
    },

    getPublishedWorkdsGrid: function() {
        if(!this._properties) {
            this._properties = Ext._create('rh.cnmp.PublishedWorksCNMPGrid', {
                title: 'Trabalhos Publicados',
            });
        }
        return this._properties;
    },

    setInformationMember: function(informationId) {
        this.informationId = informationId;
        this._observeInformationMember();
    },

    _observeInformationMember: function() {
        if(this.informationId) {
            this.getGraduation().enable();
            this.getGraduation().setFilterProperty('employee', this.informationId);
            this.getGraduation().setParam('employee', this.informationId);
            this.getGraduation().idMember = this.informationId;
            
            this.getImprovementAndGraduate().enable();
            this.getImprovementAndGraduate().setFilterProperty('employee', this.informationId);
            this.getImprovementAndGraduate().setParam('employee', this.informationId);
            this.getImprovementAndGraduate().idMember = this.informationId;

            this.getPublishedWorkdsGrid().enable();
            this.getPublishedWorkdsGrid().setFilterProperty('employee', this.informationId);
            this.getPublishedWorkdsGrid().setParam('employee', this.informationId);
            this.getPublishedWorkdsGrid().idMember = this.informationId;

        }
        else {
            this.getGraduation().getStore().removeAll();
            this.getGraduation().disable();

            this.getImprovementAndGraduate().getStore().removeAll();
            this.getImprovementAndGraduate().disable();

            this.getPublishedWorkdsGrid().getStore().removeAll();
            this.getPublishedWorkdsGrid().disable();
        }
    },

   getTabs: function() {
        if(!this._tabPanel)
            this._tabPanel = Ext._create('Ext.TabPanel', {
                region: 'south',
                height: 300,
                minHeight: 200,
                split:true,
                border: true,
                activeTab: 0,
                items: [
                    this.getGraduation(),
                    this.getImprovementAndGraduate(),
                    this.getPublishedWorkdsGrid(),
                ]
            });

        return this._tabPanel;
    },

    'getToolbar': function(cfg) {
        if(!this._toolbar) {
            adm.patrimonio.DocumentoGrid.superclass.getToolbar.call(this, cfg);

            this._toolbar.remove(10);
            this._toolbar.remove(9);
            this._toolbar.remove(8);
            this._toolbar.remove(7);
            this._toolbar.remove(6);
            this._toolbar.remove(5);
            this._toolbar.remove(4);
        }

        return this._toolbar;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                title: 'Gestor de Informações de Formação de Membros',
            }
        );

        Ext.apply(
            cfg,
            {
                border: false,
                layout: 'border',
                items: [
                    this.getInformationMember(),
                    {
                        'listeners': {
                            scope: this,
                            'render': function() {
                            }
                        },
                        region: 'south',
                        layout: 'hbox',
                        minHeight: 150,
                        height: 400,
                        split: true,
                        bodyStyle: {
                            'border-left': 0,
                            'border-right': 0
                        },
                        layoutConfig: {
                            align: 'stretch'
                        },
                        items: [
                            this.getTabs()
                        ]
                    }
                ]
            }
        );

        rh.cnmp.FormationManage.superclass.constructor.call(this, cfg);
    }
});

