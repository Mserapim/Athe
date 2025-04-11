/**
 *
 **/
Ext._define('core.GridActionWindow', {
    'extend': 'Ext.Window',

    'getGridPanel': function(cfg) {
        if(!this._gridPanel)
            if(cfg.restGrid) {
                this._gridPanel = Ext._create(cfg.restGrid, {
                    'region': 'center',
                    'disableNode': cfg.selected ? cfg.selected.id : undefined
                });
            }
            else if(cfg.rest) {
                this._gridPanel = core.RestfulGrid.factoryGrid(
                    cfg.rest,
                    {
                        'region': 'center',
                    }
                )
            }
            else
                throw 'BUG: Defina um restGrid ou um rest parametro na configuração do Objeto.'

        return this._gridPanel;
    },

    'getActionButton': function() {
        if(!this._actionButton)
            this._actionButton = Ext._create('Ext.Button', {
                'text': 'Undefined',
                'scope': this,
                'handler': function() {
                    console.warn('This class is abstract')
                }
            });

        return this._actionButton;
    },

    'constructor': function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                'callback': {},
                'title': 'Undefined',
                'width': 450,
                'modal': true,
                'layout': 'border',
                'minHeight': 200,
                'height': 400
            }
        );

        Ext.apply(
            cfg,
            {
                'items': this.getGridPanel(cfg),
                'buttons': [
                    this.getActionButton(),
                    {
                        'text': 'Cancelar',
                        'scope': this,
                        'handler': this.destroy
                    }
                ]
            }
        );

        // this.callParent([cfg]);
        core.GridActionWindow.superclass.constructor.call(this, cfg);
    }
})