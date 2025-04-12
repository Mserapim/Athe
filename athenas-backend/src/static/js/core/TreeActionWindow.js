/**
 *
 **/
Ext._define('core.TreeActionWindow', {
    'extend': 'Ext.Window',

    'getTreePanel': function(cfg) {
        if(!this._treePanel){
            var preCfg = core.nullValue(cfg.treeConfig, {});

            Ext.apply(preCfg,{
                'region': 'center',
                'disableNode': cfg.selected ? cfg.selected.id : undefined
            })
            if(cfg.restTree) {
                this._treePanel = Ext._create(cfg.restTree, preCfg);
            }
            else if(cfg.restWindow) {
                this._treePanel = Ext._create('core.RestfulTree', {
                    'region': 'center',
                    'restWindow': cfg.restWindow,
                    'folderIndexField': cfg.folderIndexField,
                    'disableNode': cfg.selected.id
                })
            }
        }

        return this._treePanel;
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
                'items': this.getTreePanel(cfg),
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
        core.TreeActionWindow.superclass.constructor.call(this, cfg);
    }
})