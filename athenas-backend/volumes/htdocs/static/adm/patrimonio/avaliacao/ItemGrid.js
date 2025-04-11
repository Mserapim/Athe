/**
 *
 **/
Ext._define('adm.patrimonio.avaliacao.ItemGrid', {
    extend: 'core.RestfulGrid',

    restWindow: 'adm.patrimonio.avaliacao.ItemWindow',

    configOrderToolBar: ['addEx', 'editEx', 'removeEx', '-', 'undo', '-', 'search', '->', 'download'],

    statics: {
        rendererUnit: function(align, unit) {
            return function(value) {
                if(value)
                    return '<div style="display:block; text-align:' + align + '">' +
                            value + ' ' + unit +
                            '</div>';
                else
                    return '';
            };
        }
    },

    getAddExAction: function(cfg) {
        if(!this._addExAction)
            this._addExAction = Ext._create('Ext.Button', {
                text: 'Novo',
                iconCls: 'icon-core icon-core-add',
                scope: this,
                handler: this.createItem
            });

        return this._addExAction;
    },

    getEditExAction: function(cfg) {
        if(!this._editExAction)
            this._editExAction = Ext._create('Ext.Button', {
                text: 'Editar',
                iconCls: 'icon-core icon-core-edit',
                scope: this,
                handler: this.updateItem
            });

        return this._editExAction;
    },

    getRemoveExAction: function(cfg) {
        if(!this._removeExAction)
            this._removeExAction = Ext._create('Ext.Button', {
                text: 'Remover',
                iconCls: 'icon-core icon-core-delete',
                scope: this,
                handler: this.removeItems
            });

        return this._removeExAction;
    },

    setEvaluateType: function(evaluateType) {
        var evaluateTypeConfig = {
            1: [false, false, false, 'adm.patrimonio.avaliacao.ItemWindow'],
            2: [true, true, true, 'adm.patrimonio.avaliacao.ManualItemWindow'],
            3: [true, true, true, 'adm.patrimonio.avaliacao.RevaluateItemWindow'],
            4: [true, true, true, 'adm.patrimonio.avaliacao.ItemWindow'], // Definir Window própria para Reversão de Depreciação
        };
        var config = evaluateTypeConfig[evaluateType];

        this.getAddExAction().setDisabled(!config[0]);
        this.getEditExAction().setDisabled(!config[1]);
        this.getRemoveExAction().setDisabled(!config[2]);
        this.restWindow = config[3];
    },

    getUndoAction: function(cfg) {
        if(!this._undoAction)
            this._undoAction = Ext._create('Ext.Button', {
                text: 'Desfazer',
                scope: this,
                handler: this.undo
            });

        return this._undoAction;
    },

    _undoRequest: function(pkset, justify) {
        var rest = this.factoryRestful();
        var mask = new Ext.LoadMask(this.getEl(), {msg: 'Desfazendo avaliação...'});

        mask.show();
        rest.doRequest(
            rest.getRoute('undo', false, 'POST', {
                scope: this,
                params: {
                    pkset: pkset,
                    justify: justify
                },
                callback: function() {
                    mask.hide();
                    mask = null;
                },
                success: function(xhr) {
                    var rst = Ext.decode(xhr.responseText);

                    if(rst.success)
                        this.getStore().reload();
                    else
                        Ext.Msg.show({
                            title: 'Desfazendo',
                            icon: Ext.Msg.ERROR,
                            buttons: Ext.Msg.OK,
                            msg: rst.message
                        });
                },
                failure: function() {
                    Ext.Msg.show({
                        title: 'Desfazendo',
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK,
                        msg: 'Recurso indisponivel no momento, tente novamente mais tarde.'
                    });
                }
            })
        );
    },

    undo: function() {
        var selected = this.getSelectionModel().getSelections();

        if(selected.length > 0) {
            Ext.Msg.prompt(
                'Justificativa',
                'Entre com a justificativa para o desfazimento da avaliação:',
                function(button, text) {
                    if(button != 'ok')
                        return;

                    this._undoRequest(
                        selected.map(function(data) { return data.get('pk'); }),
                        text
                    );
                },
                this
            );
        }
        else
            Ext.Msg.show({
                title: 'Desfazendo',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK,
                msg: 'Primeiro selecione as avaliações que deseja desfazer.'
            });
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
                        width: 105,
                        menuDisabled: true,
                        renderer: adm.daily.rendererIconGrid
                    },
                    {
                        header: 'Plaqueta',
                        dataIndex: 'plaqueta',
                        width: 75
                    },
                    {
                        header: 'Especie',
                        dataIndex: 'especie_unicode',
                        id: 'autoExpandColumn'
                    },
                    {
                        header: 'Custo',
                        dataIndex: 'custo_aquisicao',
                        width: 85,
                        renderer: toolkit.util.formatCurrency,
                        hidden: true,
                        sortable: true
                    },
                    {
                        header: 'Valor Atual',
                        dataIndex: 'valor_atual',
                        width: 85,
                        renderer: toolkit.util.formatCurrency,
                        sortable: true
                    },
                    {
                        header: 'Valor Liquido',
                        dataIndex: 'valor_avaliado',
                        width: 85,
                        renderer: toolkit.util.formatCurrency,
                        sortable: true
                    },
                    {
                        header: 'Residual',
                        dataIndex: 'residual',
                        width: 85,
                        renderer: toolkit.util.formatCurrency,
                        sortable: true
                    },
                    {
                        header: 'Variação',
                        dataIndex: 'depreciacao',
                        width: 85,
                        renderer: toolkit.util.formatCurrency,
                        sortable: true
                    },
                    {
                        header: 'Tombado',
                        dataIndex: 'data_tombo',
                        width: 75,
                        renderer: Ext.util.Format.dateRenderer('d/m/Y'),
                        hidden: true
                    },
                    {
                        header: 'Dias',
                        dataIndex: 'quantidade_dias',
                        width: 65,
                        renderer: adm.patrimonio.avaliacao.ItemGrid.rendererUnit('right', 'dia(s)'),
                        sortable: true
                    },
                    {
                        header: 'Nova vida util',
                        dataIndex: 'vida_util',
                        width: 115,
                        renderer: adm.patrimonio.avaliacao.ItemGrid.rendererUnit('right', 'ano(s)'),
                        sortable: true
                    },
                    {
                        header: 'Nova conservação',
                        dataIndex: 'conservacao_display',
                        width: 135
                    }
                ]
            );

        return this._columnModel;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(cfg, {
            viewConfig: {
                scope: this,
                getRowClass: function(record) {
                    css = [];

                    if(record.get('discarded'))
                        css.push('x-grid3-dashed');

                    return css.join(' ');
                }
            }
        });

        cfg.columnAction = false;

        adm.patrimonio.avaliacao.ItemGrid.superclass.constructor.call(this, cfg);
    }
});
