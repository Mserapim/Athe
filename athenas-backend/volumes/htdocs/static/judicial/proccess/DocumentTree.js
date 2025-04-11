/**
 *
 **/
Ext._define('judicial.proccess.DocumentTree', {
    extend: 'Ext.tree.TreePanel',

    nodeLoaderDocuments: function(node, pk) {
        var rest = Ext._create('judicial.OutCourtLawsuitRestful');

        rest.doRequest(rest.getRoute('parts', false, 'GET', {
            scope: this,
            params: {
                pk: this.lawsuitId
            },
            success: function(xhr) {
                var rst = Ext.decode(xhr.responseText);

                if(rst.success) {
                    Ext.each(
                        rst.collection,
                        function(data) {
                            node.appendChild(
                                Ext._create('Ext.tree.TreeNode', {
                                    text: data.title,
                                    id: [data.part_type, data.pk].join(':'),
                                    leaf: true,
                                    iconCls: data.iconCls
                                })
                            );
                        },
                        this
                    );
                }
            },
            failure: function() {
                Ext.Msg.show({
                    title: 'Buscando documentos',
                    icon: Ext.Msg.ERROR,
                    buttons: Ext.Msg.OK,
                    msg: 'Ocorreu um erro buscando informações do Procedimento.'
                });
            }
        }));
    },

    showContextMenu: function(node, evt) {
        console.debug(evt);
        
        var menu = Ext._create('Ext.menu.Menu', {
            items: [
                {
                    text: 'Movimento 1'
                },
                {
                    text: 'Movimento 1'
                },
                {
                    text: 'Movimento 1'
                }
            ]
        });

        menu.show();
    },

    nodeLoaderRouter: function(node) {
        var rest = Ext._create('judicial.OutCourtLawsuitRestful');
        var type, pk;

        if(node.id == 'root')
            rest.doRequest(rest.getRoute('read', this.lawsuitId, false, {
                scope: this,
                success: function(xhr) {
                    var rst = Ext.decode(xhr.responseText);

                    if(rst.success) {
                        var data = rst.instance;
                        var iconCls;

                        if(data.icons.length > 0)
                            iconCls = data.icons[0].icon;

                        node.appendChild(
                            Ext._create('Ext.tree.TreeNode', {
                                text: data.origin_assunto.toUpperCase(),
                                id: 'procedimento:' + data.pk,
                                leaf: false,
                                expandable: true,
                                iconCls: iconCls,
                                listeners: {
                                    scope: this,
                                    expand: this.nodeLoaderRouter,
                                    collapse: function(node) {
                                        node.removeAll();
                                    },
                                    contextmenu: this.showContextMenu
                                }
                            })
                        );
                    }
                },
                failure: function() {
                    Ext.Msg.show({
                        title: 'Buscando procedimento',
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK,
                        msg: 'Ocorreu um erro buscando informações do Procedimento.'
                    });
                }
            }));
        else {
            type = node.id.split(':')[0];
            pk = node.id.split(':')[1];

            if(type == 'procedimento') this.nodeLoaderDocuments(node, pk);
        }
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                rootVisible: true
            }
        );

        Ext.apply(
            cfg,
            {
                root: Ext._create('Ext.tree.TreeNode', {
                    text: 'Root',
                    leaf: false,
                    expandable: true,
                    listeners: {
                        scope: this,
                        expand: this.nodeLoaderRouter,
                        collapse: function(node) {
                            node.removeAll();
                        }
                    },
                    id: 'root'
                })
            }
        );

        // this.callParent([cfg]);
        judicial.proccess.DocumentTree.superclass.constructor.call(this, cfg);
    }
});
