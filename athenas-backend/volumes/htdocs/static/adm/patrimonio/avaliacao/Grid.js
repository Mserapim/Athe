/**
 *
 **/
Ext._define('adm.patrimonio.avaliacao.Grid', {
    extend: 'core.RestfulGrid',

    restWindow: 'adm.patrimonio.avaliacao.Window',

    constructor: function(cfg) {
        adm.patrimonio.avaliacao.Grid.superclass.constructor.call(this, cfg);

        this.getSelectionModel().on({
            scope: this,
            rowselect: function(sm, index, record) {
                this.getExecuteButton().toggle(
                    (record.get('executor') != 0),
                    true
                );
            }
        });
    },

    toggleTipo: function(tipo) {
        if(!this._filterTipo)
            this._filterTipo = [1, 2, 3, 4];

        if(this._filterTipo.indexOf(tipo) >= 0)
            this._filterTipo.remove(tipo);
        else
            this._filterTipo.push(tipo);

        this.setFilterProperty('tipo__in', this._filterTipo, 101);
    },

    getExecuteButton: function() {
        if(!this._executeButton)
            this._executeButton = Ext._create(
                'Ext.Button',
                {
                    text: 'Executa',
                    iconCls: 'icon-patrimonio icon-pat-status-bloqueado',
                    toggleGroup: 'execute',
                    scope: this,
                    toggleHandler: this.execute
                }
            );

        return this._executeButton;
    },

    execute: function(enable) {
        if(enable) {
            var rest = this.factoryRestful();
            var selected = this.getSelectionModel().getSelected();
            var mask = new Ext.LoadMask(this.getEl(), {
                msg: 'Executando...'
            });


            var conf = rest.getRoute(
                'execute',
                selected.get('pk'),
                'PUT',
                {
                    scope: this,
                    callback: function() {
                        mask.hide();
                        mask = null;
                    },
                    success: function(request) {
                        var rst = Ext.decode(request.responseText);

                        if(!rst.success) {
                            this.getExecuteButton().toggle(false, false);

                            Ext.Msg.show({
                                title: 'Avaliação de Bens',
                                icon: Ext.Msg.ERROR,
                                buttons: Ext.Msg.OK,
                                msg: rst.message
                            });
                        }
                        else
                            this.getStore().reload();
                    },
                    failure: function(request) {
                        this.getExecuteButton().toggle(false, false);

                        Ext.Msg.show({
                            title: 'Avaliação de Bens',
                            icon: Ext.Msg.ERROR,
                            buttons: Ext.Msg.OK,
                            msg: 'Ocorreu de comunicação para executar sua solicitação.'
                        });
                    }
                }
            );

            rest.doRequest(conf);
        }
        else
            Ext.Msg.show({
                title: 'Avaliação de Bens',
                icon: Ext.Msg.OK,
                buttons: Ext.Msg.ERROR,
                msg: 'Não é possiviel desfazer uma execução.'
            });
    },

    analize: function() {
        var rest = this.factoryRestful();
        var selected = this.getSelectionModel().getSelected();
        var mask = new Ext.LoadMask(this.getEl(), {
            msg: 'Executando...'
        });


        var conf = rest.getRoute(
            'analize',
            selected.get('pk'),
            'PUT',
            {
                scope: this,
                callback: function() {
                    mask.hide();
                    mask = null;
                },
                success: function(request) {
                    var rst = Ext.decode(request.responseText);

                    if(!rst.success) {
                        this.getExecuteButton().toggle(false, false);

                        Ext.Msg.show({
                            title: 'Avaliação de Bens',
                            icon: Ext.Msg.ERROR,
                            buttons: Ext.Msg.OK,
                            msg: rst.message
                        });
                    }
                    else
                        this.getStore().reload();
                },
                failure: function(request) {
                    this.getExecuteButton().toggle(false, false);

                    Ext.Msg.show({
                        title: 'Avaliação de Bens',
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK,
                        msg: 'Ocorreu de comunicação para executar sua solicitação.'
                    });
                }
            }
        );

        rest.doRequest(conf);
    },

    getToolbar: function(cfg) {
        if(!this._toolbar) {
            this._toolbar = adm.patrimonio.avaliacao.Grid.superclass.getToolbar.call(this, cfg);

            this._toolbar.insert(
                3,
                this.getExecuteButton()
            );

            this._toolbar.insert(
                3,
                ' '
            );

            this._toolbar.insert(
                3,
                {
                    iconCls: 'icon-patrimonio icon-pat-nota',
                    text: 'Analizar',
                    scope: this,
                    handler: this.analize
                }
            );

            this._toolbar.insert(
                3,
                '-'
            );
        }

        return this._toolbar;
    },

    getRoutineDepreciationFilter: function() {
        if(!this._routineDepreciation) {
            this._routineDepreciation = Ext._create('Ext.menu.CheckItem', {
                text: 'Deprecição de Rotina',
                checked: true,
                scope: this,
                handler: function() { this.toggleTipo(1); }
            });
        }

        return this._routineDepreciation;
    },

    getManualDepreciationFilter: function() {
        if(!this._manualDepreciation) {
            this._manualDepreciation = Ext._create('Ext.menu.CheckItem', {
                text: 'Depreciação manual',
                checked: true,
                scope: this,
                handler: function() { this.toggleTipo(2); }
            });
        }

        return this._manualDepreciation;
    },

    getRevaluationFilter: function() {
        if(!this._revaluation) {
            this._revaluation = Ext._create('Ext.menu.CheckItem', {
                text: 'Reavaliação',
                checked: true,
                scope: this,
                handler: function() { this.toggleTipo(3); }
            });
        }

        return this._revaluation;
    },

    getDepreciationReversalFilter: function() {
        if(!this._depreciationReversal) {
            this._depreciationReversal = Ext._create('Ext.menu.CheckItem', {
                text: 'Reversão de Depreciação',
                checked: true,
                scope: this,
                handler: function() { this.toggleTipo(4); }
            });
        }

        return this._depreciationReversal;
    },

    getMarkAllFilter: function() {
        if(!this._markAll) {
            this._markAll = Ext._create('Ext.menu.Item', {
                text: 'Selecionar Todos',
                scope: this,
                hideOnClick: false,
                handler: function() {
                    this.getRoutineDepreciationFilter().setChecked(true);
                    this.getManualDepreciationFilter().setChecked(true);
                    this.getRevaluationFilter().setChecked(true);
                    this.getDepreciationReversalFilter().setChecked(true);

                    this._filterTipo = [1, 2, 3, 4];
                    this.removeFilterProperty('tipo__in', 101, false);
                    this.setFilterProperty('tipo__in', this._filterTipo, 101, true);
                }
            });
        }

        return this._markAll;
    },

    getUnmarkAllFilter: function() {
        if(!this._unmarkAll) {
            this._unmarkAll = Ext._create('Ext.menu.Item', {
                text: 'Desmarcar Todos',
                scope: this,
                hideOnClick: false,
                handler: function() {
                    this.getRoutineDepreciationFilter().setChecked(false);
                    this.getManualDepreciationFilter().setChecked(false);
                    this.getRevaluationFilter().setChecked(false);
                    this.getDepreciationReversalFilter().setChecked(false);

                    this._filterTipo = [];
                    this.removeFilterProperty('tipo__in', 101, false);
                    this.setFilterProperty('tipo__in', this._filterTipo, 101, true);
                }
            });
        }

        return this._unmarkAll;
    },

    getFilterMenu: function() {
        if(!this._filterMenu)
            this._filterMenu = [
                this.getRoutineDepreciationFilter(),
                this.getManualDepreciationFilter(),
                this.getRevaluationFilter(),
                this.getDepreciationReversalFilter(),
                '-',
                this.getMarkAllFilter(),
                this.getUnmarkAllFilter()
            ];

        return this._filterMenu;
    },

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    {
                        header: '',
                        dataIndex: 'icons',
                        width: 50,
                        menuDisabled: true,
                        renderer: adm.daily.rendererIconGrid
                    },
                    {
                        header: 'Tipo',
                        dataIndex: 'tipo_display',
                        width: 175
                    },
                    {
                        header: 'Competencia',
                        dataIndex: 'competencia',
                        width: 95
                    },
                    {
                        header: 'Numero',
                        dataIndex: 'number_formated',
                        width: 95
                    },
                    {
                        header: 'Tabela',
                        dataIndex: 'tabela_unicode',
                        id: 'autoExpandColumn'
                    },
                    {
                        header: 'Excutado por',
                        dataIndex: 'executor_unicode',
                        width: 175
                    },
                    {
                        header: 'Apartir de',
                        dataIndex: 'de',
                        width: 115,
                        renderer: Ext.util.Format.dateRenderer('d/m/Y H:i')
                    },
                    {
                        header: 'Até',
                        dataIndex: 'ate',
                        width: 115,
                        renderer: Ext.util.Format.dateRenderer('d/m/Y H:i')
                    }
                ]
            );

        return this._columnModel;
    }
});
