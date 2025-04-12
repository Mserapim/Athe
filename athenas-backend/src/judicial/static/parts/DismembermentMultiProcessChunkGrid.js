
Ext._define('judicial.parts.DismembermentMultiProcessChunkGrid', {
    extend: 'core.RestfulGrid',
    restWindow: 'judicial.parts.DismembermentMultiProcessChunkWindow'
});


core.RestfulGrid.register(
    'judicial.parts.DismembermentMultiProcessChunkRestful',
    'judicial.parts.DismembermentMultiProcessChunkGrid'
);
