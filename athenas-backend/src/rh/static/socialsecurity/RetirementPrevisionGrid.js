Ext._define('rh.socialsecurity.RetirementPrevisionGrid', {
    extend: 'core.RestfulGrid',

    restWindow: 'rh.socialsecurity.RetirementPrevisionWindow',

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    {header: '', dataIndex: 'icons', width: 107, renderer: core.rendererIconGrid, menuDisabled: true},
                    {header: 'Contribuinte', dataIndex: 'natural_person_unicode', id: 'autoExpandColumn', sortable: true},
                    {header: 'Ocupação', dataIndex: 'last_occupation_unicode', width: 400, sortable: true},
                    {header: 'Nascimento', dataIndex: 'birth_date', renderer: Ext.util.Format.dateRenderer('d/m/Y'), width: 75, sortable: true},
                    {header: 'Idade', dataIndex: 'age', width: 45, sortable: true},
                    {header: 'Data de exercício', dataIndex: 'exercise_date', renderer: Ext.util.Format.dateRenderer('d/m/Y'), width: 100, sortable: true},
                    {header: 'Aposent. - Contribuição', dataIndex: 'contribution_prevision_date', renderer: Ext.util.Format.dateRenderer('d/m/Y'), width: 130, sortable: true},
                    {header: 'Aposent. - Idade', dataIndex: 'age_prevision_date', renderer: Ext.util.Format.dateRenderer('d/m/Y'), width: 95, sortable: true},
                    {header: 'Aposent. Integral', dataIndex: 'integral_prevision_date', renderer: Ext.util.Format.dateRenderer('d/m/Y'), width: 100, sortable: true},
                    {header: 'Total RGPS', dataIndex: 'rgps_liquid_days', width: 70, sortable: true},
                    {header: 'Total RPPS', dataIndex: 'rpps_liquid_days', width: 70, sortable: true}
                ]
            );

        return this._columnModel;
    },

    getFilterMenu: function() {
        return [
            {
                text: 'Status',
                menu: [
                    {
                        text: 'Membro',
                        checked: true,
                        scope: this,
                        hideOnClick: false,
                        handler: function() { this.toggleStatus('M'); }
                    },
                    {
                        text: 'Servidor',
                        checked: true,
                        scope: this,
                        hideOnClick: false,
                        handler: function() { this.toggleStatus('S'); }
                    }
                ]
            },
            {
                text: 'Sexo',
                menu: [
                    {
                        text: 'Masculino',
                        checked: true,
                        scope: this,
                        hideOnClick: false,
                        handler: function() { this.toggleSex('M'); }
                    },
                    {
                        text: 'Feminino',
                        checked: true,
                        scope: this,
                        hideOnClick: false,
                        handler: function() { this.toggleSex('F'); }
                    }
                ]
            },
            {
                text: 'Atividade',
                menu: [
                    {
                        text: 'Ativo',
                        checked: true,
                        scope: this,
                        hideOnClick: false,
                        handler: function() { this.toggleActive(true); }
                    },
                    {
                        text: 'Inativo',
                        checked: true,
                        scope: this,
                        hideOnClick: false,
                        handler: function() { this.toggleActive(false); }
                    }
                ]
            },
            {
                text: 'Anterior a EC 20/98',
                menu: [
                    {
                        text: 'Sim',
                        checked: true,
                        scope: this,
                        hideOnClick: false,
                        handler: function() { this.toggleAppliesOldPensionRule(true); }
                    },
                    {
                        text: 'Não',
                        checked: true,
                        scope: this,
                        hideOnClick: false,
                        handler: function() { this.toggleAppliesOldPensionRule(false); }
                    }
                ]
            },
            {
                text: 'Negativa de vínculo anterior',
                checked: false,
                scope: this,
                hideOnClick: false,
                handler: function() { this.toggleNegativePreviousBond(false); }
            },
            {
                text: 'Aposentadoria - Integral',
                scope: this,
                handler: this.filterIntegralPrevisionDate
            },
            {
                text: 'Aposentadoria - Idade',
                scope: this,
                handler: this.filterAgePrevisionDate
            },
            {
                text: 'Aposentadoria - Contribuição',
                scope: this,
                handler: this.filterContributionPrevisionDate
            },
        ];
    },

    toggleStatus: function(tipo) {
        if(!this._filterStatus)
            this._filterStatus = ['M', 'S'];

        if(this._filterStatus.indexOf(tipo) >= 0)
            this._filterStatus.remove(tipo);
        else
            this._filterStatus.push(tipo);

        this.setFilterProperty('natural_person__servidor__tipo__in', this._filterStatus, 1000);
    },

    toggleSex: function(tipo) {
        if(!this._filterSex)
            this._filterSex = ['M', 'F'];

        if(this._filterSex.indexOf(tipo) >= 0)
            this._filterSex.remove(tipo);
        else
            this._filterSex.push(tipo);

        this.setFilterProperty('natural_person__sexo__in', this._filterSex, 1001);
    },

    toggleActive: function(tipo) {
        if(!this._filterActive)
            this._filterActive = [true, false];

        if(this._filterActive.indexOf(tipo) >= 0)
            this._filterActive.remove(tipo);
        else
            this._filterActive.push(tipo);

        this.setFilterProperty('active__in', this._filterActive, 1002);
    },

    toggleAppliesOldPensionRule: function(tipo) {
        if(!this._filterActive)
            this._filterActive = [true, false];

        if(this._filterActive.indexOf(tipo) >= 0)
            this._filterActive.remove(tipo);
        else
            this._filterActive.push(tipo);

        this.setFilterProperty('before_ec_20_98__in', this._filterActive, 1003);
    },

    toggleNegativePreviousBond: function(tipo) {
        if(!this._filterNegativePreviousBond)
            this._filterNegativePreviousBond = [true, false];

        if(this._filterNegativePreviousBond.indexOf(tipo) >= 0)
            this._filterNegativePreviousBond.remove(tipo);
        else
            this._filterNegativePreviousBond.push(tipo);

        this.setFilterProperty('negative_previous_bond__in', this._filterNegativePreviousBond, 1004);
    },

    filterIntegralPrevisionDate: function() {
        var wnd = Ext._create('Ext.Window', {
            title: 'Aposentadoria - Integral',
            width: 250,
            modal: true,
            border: false,
            items: [
                Ext._create('Ext.form.FormPanel', {
                    border: false,
                    frame: true,
                    items: [
                        {
                            fieldLabel: 'De',
                            name: 'from',
                            xtype: 'datefield',
                            allowBlank: true
                        },
                        {
                            fieldLabel: 'Até',
                            name: 'to',
                            xtype: 'datefield',
                            allowBlank: true
                        }
                    ]
                })
            ],
            buttons: [
                {
                    text: 'Selecionar',
                    scope: this,
                    handler: function() {
                        var form = wnd.getComponent(0).getForm();
                        var date = {
                            from: Ext.util.Format.date(form.findField('from').getValue(), 'Y-m-d'),
                            to: Ext.util.Format.date(form.findField('to').getValue(), 'Y-m-d')
                        };

                        if(date.from !== '')
                            this.setFilterProperty('integral_prevision_date__gte', date.from, 1005, false);
                        else
                            this.removeFilterProperty('integral_prevision_date__gte', 1005, false);

                        if(date.to !== '')
                            this.setFilterProperty('integral_prevision_date__lte', date.to, 1006, false);
                        else
                            this.removeFilterProperty('integral_prevision_date__lte', 1006, false);

                        this.getStore().load({});
                        wnd.destroy();
                    }
                },
                {
                    text: 'Fechar',
                    handler: function() { wnd.destroy(); }
                }
            ]
        }).show();
    },

    filterAgePrevisionDate: function() {
        var wnd = Ext._create('Ext.Window', {
            title: 'Aposentadoria - Integral',
            width: 250,
            modal: true,
            border: false,
            items: [
                Ext._create('Ext.form.FormPanel', {
                    border: false,
                    frame: true,
                    items: [
                        {
                            fieldLabel: 'De',
                            name: 'from',
                            xtype: 'datefield',
                            allowBlank: true
                        },
                        {
                            fieldLabel: 'Até',
                            name: 'to',
                            xtype: 'datefield',
                            allowBlank: true
                        }
                    ]
                })
            ],
            buttons: [
                {
                    text: 'Selecionar',
                    scope: this,
                    handler: function() {
                        var form = wnd.getComponent(0).getForm();
                        var date = {
                            from: Ext.util.Format.date(form.findField('from').getValue(), 'Y-m-d'),
                            to: Ext.util.Format.date(form.findField('to').getValue(), 'Y-m-d')
                        };

                        if(date.from !== '')
                            this.setFilterProperty('age_prevision_date__gte', date.from, 1007, false);
                        else
                            this.removeFilterProperty('age_prevision_date__gte', 1007, false);

                        if(date.to !== '')
                            this.setFilterProperty('age_prevision_date__lte', date.to, 1008, false);
                        else
                            this.removeFilterProperty('age_prevision_date__lte', 1008, false);

                        this.getStore().load({});
                        wnd.destroy();
                    }
                },
                {
                    text: 'Fechar',
                    handler: function() { wnd.destroy(); }
                }
            ]
        }).show();
    },

    filterContributionPrevisionDate: function() {
        var wnd = Ext._create('Ext.Window', {
            title: 'Aposentadoria - Contribuição',
            width: 250,
            modal: true,
            border: false,
            items: [
                Ext._create('Ext.form.FormPanel', {
                    border: false,
                    frame: true,
                    items: [
                        {
                            fieldLabel: 'De',
                            name: 'from',
                            xtype: 'datefield',
                            allowBlank: true
                        },
                        {
                            fieldLabel: 'Até',
                            name: 'to',
                            xtype: 'datefield',
                            allowBlank: true
                        }
                    ]
                })
            ],
            buttons: [
                {
                    text: 'Selecionar',
                    scope: this,
                    handler: function() {
                        var form = wnd.getComponent(0).getForm();
                        var date = {
                            from: Ext.util.Format.date(form.findField('from').getValue(), 'Y-m-d'),
                            to: Ext.util.Format.date(form.findField('to').getValue(), 'Y-m-d')
                        };

                        if(date.from !== '')
                            this.setFilterProperty('contribution_prevision_date__gte', date.from, 1009, false);
                        else
                            this.removeFilterProperty('contribution_prevision_date__gte', 1009, false);

                        if(date.to !== '')
                            this.setFilterProperty('contribution_prevision_date__lte', date.to, 1010, false);
                        else
                            this.removeFilterProperty('contribution_prevision_date__lte', 1010, false);

                        this.getStore().load({});
                        wnd.destroy();
                    }
                },
                {
                    text: 'Fechar',
                    handler: function() { wnd.destroy(); }
                }
            ]
        }).show();
    },

    cleanFilter: function() {
        try {
            this.setFilterProperty('natural_person__servidor__tipo__in', ['M', 'S'], 1000, false);
            this.setFilterProperty('natural_person__sexo__in', ['M', 'F'], 1001, false);
            this.setFilterProperty('active__in', [true, false], 1002, false);
            this.setFilterProperty('before_ec_20_98__in', [true, false], 1003, false);
            this.setFilterProperty('negative_previous_bond__in', [true, false], 1004, false);
        }
        catch(e) { /* não faz nada */ }
    }
});

core.RestfulGrid.register(
    'rh.socialsecurity.RetirementPrevisionRestful',
    'rh.socialsecurity.RetirementPrevisionGrid'
);
