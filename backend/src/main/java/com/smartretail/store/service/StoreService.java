package com.smartretail.store.service;

import com.smartretail.store.dto.CreateStoreRequest;
import com.smartretail.store.dto.StoreResponse;
import com.smartretail.store.entity.Store;
import com.smartretail.store.repository.StoreRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
@Transactional
public class StoreService {

    private final StoreRepository storeRepository;

    public StoreService(StoreRepository storeRepository) {
        this.storeRepository = storeRepository;
    }

    public StoreResponse createStore(CreateStoreRequest request) {
        Store store = new Store(request.name().trim(), request.location().trim());
        Store savedStore = storeRepository.save(store);
        return StoreResponse.fromEntity(savedStore);
    }

    @Transactional(readOnly = true)
    public List<StoreResponse> getAllStores() {
        return storeRepository.findAll()
                .stream()
                .map(StoreResponse::fromEntity)
                .toList();
    }
}
