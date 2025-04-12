Ext._define('corregedoria.cirdir.evaluator.Grid', {
    extend: 'core.RestfulGrid',
    restWindow: 'corregedoria.cirdir.evaluator.Window',

    configOrderToolBar: ['add', 'edit', 'remove','-', 'delivery', ],

    getDeliveryAction: function(cfg) {
        if(!this._deleryAction) {
            this._deleryAction = new Ext.Button({
                xtype: 'button',
                text: 'Distribuir',
                iconCls: 'icon-crgmpe icon-crgmpe-list',
                scope: this,
                handler: function() {
                    this.deliveryToEvaluators(
                        this.getSelectionModel().getSelections(),
                        this.getHealthOriginGrid().getSelectionModel().getSelections()
                    );
                }
            });
        }
        return this._deleryAction;
    },

    deliveryToEvaluators: function (evaluators, healths) {

        fn = ( function (data) {
            var list = [];
            data.forEach(function(v){
                list.push(v.get('pk'));
            });
            return list;
        });

        evaluators = fn(evaluators);
        healths = fn(healths);

        if(evaluators.length > 0 && healths.length > 0)
            this.delivery(evaluators, healths);
        else
            Ext.Msg.show({
                title: 'Distribuir',
                msg: 'Verifique se o avaliador e o questionário estão selecionados',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK
            });
    },

    delivery: function(evaluators, healths) {
        var rest = this.factoryRestful();
        var mask = new Ext.LoadMask(this.getEl(), {msg: 'Atribuindo a um avaliador...'});

        mask.show();
        rest.delivery(
            evaluators,
            healths,
            {
                scope: this,
                fn: function(rst) {
                    Ext.Msg.show({
                        title: 'Concluindo',
                        msg: rst.message,
                        icon: Ext.Msg.INFO,
                        buttons: Ext.Msg.OK
                    });
                }
            },
            {
                scope: this,
                fn: function(message) {
                    Ext.Msg.show({
                        title: 'Concluindo',
                        msg: message,
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK
                    });
                }
            },
            {
                scope: this,
                fn: function() {
                    core.invokeCallback((this.callback || {}).success);
                    this.getHealthOriginGrid().getStore().load();
                    mask.hide();
                }
            }
        );
    },

    getHealthOriginGrid: function() {
        return this._healthOriginGrid;
    },

    setHealthOriginGrid: function(grid) {
        if(!this._healthOriginGrid)
            this._healthOriginGrid = grid;
    },

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    {header: '', dataIndex: 'icons', width: 50, renderer: core.rendererIconGrid},
                    {header: 'Avaliador', dataIndex: 'employee_unicode', id: 'autoExpandColumn'}
                ]
            );

        return this._columnModel;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                columnAction: false
            }
        );
        corregedoria.cirdir.evaluator.Grid.superclass.constructor.call(this, cfg);
    }

});

core.RestfulGrid.register(
    'corregedoria.cirdir.evaluator.Restful',
    'corregedoria.cirdir.evaluator.Grid'
);
