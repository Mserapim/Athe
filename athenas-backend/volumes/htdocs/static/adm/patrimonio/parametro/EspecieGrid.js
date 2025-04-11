/**
 *
 **/
Ext._define('adm.patrimonio.parametro.EspecieGrid', {
    extend: 'core.RestfulGrid',

    restWindow: 'adm.patrimonio.parametro.EspecieWindow',

    keywordFieldMessage: 'Descrição ou código.',

    configOrderToolBar: ['add', 'edit', 'remove', 'moverGrupo',  '-', 'search',  '->'],

    getMoverGrupoAction: function(){
        this.mover_grupo = Ext._create('Ext.Button', {
            text: 'Mover',
            iconCls: 'icon-patrimonio icon-pat-avaliacao-positiva',
            scope: this,
            handler: this.getMovimentar
        });

        return this.mover_grupo;

    },

    getMovimentar: function(){
        var selections = this.getSelectionModel().getSelections();
        if(selections.length > 0) {
            var wnd = Ext._create('adm.patrimonio.parametro.EspecieMovimentacaoWindow', {
                modal: true,
                scope:this,
                params: {
                    pks: selections.map(function(item) { return item.get('pk'); })
                },
                callback: {
                    success: {
                        scope: this,
                        fn: function() {
                            this.getStore().reload();
                        }
                    }
                }
            });
            wnd.show();

        }else{
            Ext.Msg.show({
                title: 'Atenção',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK,
                msg: 'Selecione pelo menos um item.'
            });
        }
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
                        width: 40,
                        menuDisabled: true,
                        renderer: adm.daily.rendererIconGrid
                    },
                    {header: 'Codigo', dataIndex: 'codigo_cache', width: 60},
                    {header: 'Descrição', dataIndex: 'titulo', id: 'autoExpandColumn'}
                ]
            );

        return this._columnModel;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
            }
        );

        Ext.apply(
            cfg,
            {
            }
        );

        // this.callParent([cfg]);
        adm.patrimonio.parametro.EspecieGrid.superclass.constructor.call(this, cfg);
    }
});

core.RestfulGrid.register(
    'adm.patrimonio.parametro.EspecieRestful',
    'adm.patrimonio.parametro.EspecieGrid'
);
