
/**
 *
 **/
Ext._define('edocs.processo.ProcessScopeTree', {
    extend: 'Ext.tree.TreePanel',

    loadTypeLawSuit: function(root) {
        var data = [
            {
                value: 1,
                description: 'Caixa de Entrada',
                slug: 'icon-core icon-core-add-all',
                type: 'type_box'
            },
            {
                value: 2,
                description: 'Caixa de Saída',
                slug: 'icon-core icon-core-remove-all',
                type: 'type_box'
            },

        ];

        Ext.each(
            data,
            function(row) {
                var node = Ext._create('Ext.tree.TreeNode', {
                    value: row.value,
                    node: row.slug,
                    text: row.description,
                    type: row.type,
                    iconCls: row.slug
                });
                root.appendChild(node);
            }
        );
    },


    _employee: function(value) {
        this.employee = value;
    },

    loadWorkLocations: function() {
        var root = this.getRootNode();

        Ext.Ajax.request({
            url: core.callAction('EDOCManage', 'work_locations'),
            scope: this,
            success: function(xhr) {
                var rst = Ext.decode(xhr.responseText);
                if(rst.success) {
                    this._employee(rst.collection[0].employee);
                    Ext.each(
                        rst.collection,
                        function(record) {
                            var node = Ext._create('Ext.tree.TreeNode', {
                                id: record.pk,
                                node: record.pk,
                                text: record.description,
                                type: 'location',
                                expanded: true
                                // iconCls: 'icon-judicial icon-ejud-departament'
                            });

                            this.loadTypeLawSuit(node);
                            root.appendChild(node);
                        },
                        this
                    );
                }
                else
                    Ext.Msg.show({
                        title: 'Locais de Trabalho',
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK,
                        msg: rst.message
                    });
            },
            failure: function(xhr) {
                Ext.Msg.show({
                    title: 'Locais de Trabalho',
                    icon: Ext.Msg.ERROR,
                    buttons: Ext.Msg.OK,
                    msg: 'Ocorreu um erro tentando baixar os locais de Trabalho.'
                });
            }
        });
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                rootVisible: false
            }
        );

        Ext.apply(
            cfg,
            {
                tbar: [

                    {
                        text: 'Limpar filtro',
                        iconCls: 'icon-core icon-core-clear',
                        scope: this,
                        handler: function(cfg) {
                            this.grid_entrada.removeFilterProperty('lotacao_destino', 1000);
                            this.grid_saida.removeFilterProperty('lotacao_origem', 1000);
                        }
                    }
                ],
                root: Ext._create('Ext.tree.TreeNode', {
                    text: 'Atuação',
                    leaf: false,
                }),
                listeners: {
                    scope: this,
                    render: this.loadWorkLocations
                }
            }
        );

        // this.callParent([cfg]);
        edocs.processo.ProcessScopeTree.superclass.constructor.call(this, cfg);
    }
});
